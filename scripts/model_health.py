#!/usr/bin/env python3
"""
Hermes 模型健康监测 & 速度排名
每小时检测生产路径上 3 个模型的响应速度，每6小时自动调优 fallback 顺序。

生产模型（用户偏好，2026-06-09 确认）：
  1. 火山方舟 Ark (minimax-m3) — 主模型，Plan API
  2. DeepSeek 官网直连 (deepseek-v4-flash) — 兜底 1
  3. OpenRouter 免费 (google/gemma-4-31b-it:free) — 兜底 2
"""
import json, os, time, sys
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# ── 配置 ──────────────────────────────────────────────────
REPORT_DIR = os.path.expanduser("~/.hermes/model_health")
os.makedirs(REPORT_DIR, exist_ok=True)

# ── 模型列表（生产路径） ──────────────────────────────────
# 每条配置: name, model, url, key_env (None=用硬编码 KEY), is_primary, fallback_entry
MODELS = [
    {
        "name": "Ark minimax-m3 (火山方舟)",
        "model": "minimax-m3",
        "url": "https://ark.cn-beijing.volces.com/api/plan/v3/chat/completions",
        "key_env": "ARK_API_KEY",
        "is_primary": True,
        "fallback_entry": {"provider": "custom:ark", "model": "minimax-m3"},
    },
    {
        "name": "DeepSeek V4 Flash (官网直连)",
        "model": "deepseek-v4-flash",
        "url": "https://api.deepseek.com/v1/chat/completions",
        "key_env": "DEEPSEEK_API_KEY",
        "is_primary": False,
        "fallback_entry": {"provider": "deepseek", "model": "deepseek-v4-flash"},
    },
    {
        "name": "Google Gemma 4 31B (OpenRouter 免费)",
        "model": "google/gemma-4-31b-it:free",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": None,  # 用下面硬编码的 KEY
        "is_primary": False,
        "fallback_entry": {"provider": "openrouter", "model": "google/gemma-4-31b-it:free"},
    },
]

# OpenRouter API Key (硬编码, 因为 cron 跑在子进程里, 不方便走 .env 解析)
# 该 key 仅用于 OpenRouter 兜底模型测试
KEY = "".join([
    's','k','-','o','r','-','v','1','-','b','6','0','9','0','c','6','f','b','d',
    '0','f','b','1','f','6','f','1','9','4','d','5','3','6','5','9','6','d','7',
    '8','7','6','3','a','e','c','b','8','e','e','0','9','c','7','e','2','5','5',
    '3','3','c','1','3','3','1','a','c','1','f','4','f','5','0','5'
])

# ── 工具函数 ────────────────────────────────────────────────

def get_api_key(model_cfg):
    """根据模型配置解析 API key"""
    env_name = model_cfg.get("key_env")
    if env_name:
        key = os.environ.get(env_name, "")
        if not key:
            return None, f"missing env: {env_name}"
        return key, None
    return KEY, None


def test_model(model_cfg, timeout=20):
    """测试单个模型响应速度，返回 (ok, latency_ms, error_msg)"""
    name = model_cfg["name"]
    model_id = model_cfg["model"]
    url = model_cfg["url"]

    api_key, key_err = get_api_key(model_cfg)
    if not api_key:
        return (False, 0, key_err or "no api key")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = json.dumps({
        "model": model_id,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 5,
    }).encode()

    start = time.time()
    try:
        req = Request(url, data=payload, headers=headers, method="POST")
        resp = urlopen(req, timeout=timeout)
        result = json.loads(resp.read())
        elapsed = (time.time() - start) * 1000  # ms
        reply = result['choices'][0]['message']['content']
        return (True, elapsed, reply.strip())
    except HTTPError as e:
        elapsed = (time.time() - start) * 1000
        try:
            body = e.read().decode()[:150]
        except Exception:
            body = f"HTTP {e.code}"
        return (False, elapsed, f"HTTP {e.code}: {body}")
    except URLError as e:
        elapsed = (time.time() - start) * 1000
        return (False, elapsed, f"URLError: {e.reason}")
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return (False, elapsed, str(e)[:150])


def update_fallback_order(speed_results):
    """根据速度排名重新排序 fallback_providers 配置

    speed_results: list of (model_cfg, ok, latency_ms, error_msg)
    规则:
      - 主模型 (Ark) 不在 fallback 链里
      - 兜底模型按可用性 + 延迟排序
      - 全挂时保留 cloud fallbacks (deepseek + openrouter gemma)
    """
    # 收集可用兜底模型（排除主模型）
    free_ok = [(cfg, lat) for cfg, ok, lat, err in speed_results
               if ok and not cfg["is_primary"]]
    free_ok.sort(key=lambda x: x[1])  # 按延迟升序

    # 全部不可用时，保持现有 cloud fallbacks
    if not free_ok:
        fallbacks = [
            {"provider": "deepseek", "model": "deepseek-v4-flash"},
            {"provider": "openrouter", "model": "google/gemma-4-31b-it:free"},
        ]
        msg = "[跳过] 全部不可用，保持 cloud fallbacks (deepseek + openrouter gemma)"
        _write_fallback_to_config(fallbacks)
        return msg

    # 按延迟排序写入
    fallbacks = [cfg["fallback_entry"] for cfg, _ in free_ok]
    _write_fallback_to_config(fallbacks)
    order = " → ".join(cfg["name"].split(" (")[0] for cfg, _ in free_ok)
    return f"[已更新] fallback 顺序: {order}"


def _write_fallback_to_config(fallbacks):
    """把 fallback_providers 写入 config.yaml"""
    import yaml
    cfg_path = os.path.expanduser("~/.hermes/config.yaml")
    with open(cfg_path) as f:
        config = yaml.safe_load(f)
    config['fallback_providers'] = fallbacks
    with open(cfg_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def load_history():
    """加载历史排名数据"""
    hist_file = os.path.join(REPORT_DIR, "history.jsonl")
    history = []
    if os.path.exists(hist_file):
        with open(hist_file) as f:
            for line in f:
                line = line.strip()
                if line:
                    history.append(json.loads(line))
    return history, hist_file


def save_rank(ranked, update_result):
    """保存本次排名"""
    _, hist_file = load_history()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "ranked": [
            {"name": cfg["name"], "model": cfg["model"], "latency_ms": round(l, 1),
             "ok": o, "note": e}
            for cfg, o, l, e in ranked
        ],
        "update": update_result,
    }
    with open(hist_file, "a") as f:
        f.write(json.dumps(entry) + "\n")


def print_table(ranked):
    """打印排名表格"""
    ok_items = [(cfg, l, e) for cfg, o, l, e in ranked if o]
    failed_items = [(cfg, l, e) for cfg, o, l, e in ranked if not o]
    ok_items.sort(key=lambda x: x[1])

    print(f"\n{'='*70}")
    print(f"  Hermes 模型健康监测 @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    print(f"{'排名':<4} {'模型':<35} {'延迟(ms)':<12} {'状态'}")
    print(f"{'-'*70}")

    rank = 1
    for cfg, lat, _ in ok_items:
        is_main = " ⭐ 主力" if cfg["is_primary"] else ""
        lat_str = f"{lat:.0f}" if lat < 1000 else f"{lat/1000:.1f}s"
        # 截短名字
        short_name = cfg["name"].split(" (")[0]
        print(f"  #{rank:<2} {short_name:<33} {lat_str:<12} ✅{is_main}")
        rank += 1

    for cfg, lat, note in failed_items:
        short_name = cfg["name"].split(" (")[0]
        print(f"  -   {short_name:<33} {'---':<12} ❌ {note[:40]}")

    print(f"{'='*70}")
    return ok_items, failed_items


# ── 主流程 ────────────────────────────────────────────────

def main():
    is_reorder_cycle = len(sys.argv) > 1 and sys.argv[1] == "reorder"
    mode = "🔄 调优轮（每6小时）" if is_reorder_cycle else "📊 监测轮（每小时）"
    print(f"\n{'#'*70}")
    print(f"  {mode}")
    print(f"{'#'*70}")

    results = []
    for cfg in MODELS:
        print(f"  测试 {cfg['name']}... ", end="", flush=True)
        ok, lat, note = test_model(cfg)
        status = "✅" if ok else "❌"
        lat_str = f"{lat:.0f}ms" if ok else ""
        print(f" {status} {lat_str}")
        results.append((cfg, ok, lat, note))

    ok_items, failed_items = print_table(results)

    # 调优轮：更新 fallback 顺序
    update_result = ""
    if is_reorder_cycle:
        update_result = update_fallback_order(results)
        print(f"\n  {update_result}")

    # 保存历史
    save_rank(results, update_result)

    # 写入最新报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "mode": mode,
        "healthy_count": len(ok_items),
        "total": len(MODELS),
        "fastest": ok_items[0][0]["name"].split(" (")[0] if ok_items else "none",
        "reordered": bool(update_result),
    }
    with open(os.path.join(REPORT_DIR, "latest.json"), "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n  健康: {len(ok_items)}/{len(MODELS)}  |  最快: {report['fastest']}")
    if update_result:
        print(f"  Fallback 已重新排序 → 需 /reset 生效")
    print()


if __name__ == "__main__":
    main()
