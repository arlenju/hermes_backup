---
name: install-local-vision-mlx
description: Install a local MLX vision-language model on Apple Silicon as Hermes' vision backend, with launchd auto-start and KeepAlive crash recovery. Use when user wants to set up or switch local vision (let the agent "see" images) using mlx_vlm + Qwen3-VL or similar VLM models.
version: 1.0.0
author: Hermes Agent + 鞠帅
license: MIT
platforms: [macos]
prerequisites:
  commands: [python, launchctl]
  os: macos
metadata:
  hermes:
    tags: [vision, mlx, apple-silicon, vlm, qwen3-vl, local-inference, launchd]
    proven_on: [macOS 26.3 (Tahoe), M5 24GB, Qwen3-VL-8B-Instruct-6bit]
---

# 安装本地 MLX 视觉模型 (Apple Silicon)

让 Hermes Agent 真正能"看图"——不依赖远程 API，用本地 MLX 跑视觉语言模型，OpenAI 兼容服务，launchd 开机自启 + 崩溃自愈。

**适用场景：**
- 用户在 M 系列 Mac 上想装本地视觉模型
- 想把 Hermes 的 `vision_analyze` / 视觉链路切到本地
- 需要服务一直在跑（不依赖手动 lms server start 之类）

**已验证组合：** macOS 26.3 + M5/24GB + `mlx-community/Qwen3-VL-8B-Instruct-6bit` (7.3GB)

---

## 模型选型建议

| 内存 | 推荐 | 大小 |
|---|---|---|
| 16GB | `mlx-community/Qwen3-VL-4B-Instruct-6bit` | ~3.5GB |
| **24GB** | **`mlx-community/Qwen3-VL-8B-Instruct-6bit`** ⭐ | ~7.3GB |
| 32GB+ | `mlx-community/Qwen3-VL-8B-Instruct-8bit` | ~8.5GB |
| 64GB+ | `mlx-community/Qwen3-VL-30B-A3B-Instruct-6bit` | ~24GB |

**为什么选 6bit MLX**：M 系芯片上 MLX 比 GGUF 快 30-50%，6-bit 量化质量接近原版，速度比 8-bit 快很多。

---

## 步骤

### 1️⃣ 安装 mlx-vlm 推理后端

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
pip install mlx-vlm mlx-lm
```

⚠️ **必须装到 Hermes runtime venv** (`~/.hermes/hermes-agent/venv/`)，不是项目 dev venv。

### 2️⃣ 下载模型（用 aria2c 多线程，不用 hf-cli）

**为什么不用 hf download：** HF 新的 xet 协议在境内极易卡死/限速 3-4MB/s，经常下到一半 TCP 连接 CLOSED 但进程不退出。**aria2c 是唯一可靠的方案**。

```bash
MODEL=mlx-community/Qwen3-VL-8B-Instruct-6bit
DEST=~/.lmstudio/models/$MODEL
mkdir -p "$DEST" && cd "$DEST"

# 1. 先用 hf 下载小文件（tokenizer/config，几个MB）
source ~/.hermes/hermes-agent/venv/bin/activate
hf download $MODEL --local-dir . --include "*.json" --include "*.txt" --include "*.jinja"

# 2. 大文件 safetensors 用 aria2c (Motrix 自带，已验证可靠)
ARIA=/Applications/Motrix.app/Contents/Resources/engine/aria2c
for FILE in $(curl -s https://huggingface.co/$MODEL/raw/main/model.safetensors.index.json | python3 -c "import json,sys;print('\n'.join(set(json.load(sys.stdin)['weight_map'].values())))"); do
  URL=$(curl -sIL -o /dev/null -w "%{url_effective}" "https://huggingface.co/$MODEL/resolve/main/$FILE")
  $ARIA -x 16 -s 16 -k 1M \
    --file-allocation=none --continue=true --max-tries=20 --retry-wait=10 \
    --connect-timeout=30 --timeout=60 \
    --lowest-speed-limit=100K \
    -o "$FILE" "$URL" &
done
wait
echo "✅ 下载完成"
```

**关键参数：**
- `-x 16 -s 16`：16 个连接并行
- `--lowest-speed-limit=100K`：网速低于 100KB/s 主动重连（治"进程活着但不下载"卡死症）
- `--max-tries=20 --retry-wait=10`：断了重试 20 次
- `--file-allocation=none`：跳过文件预分配

**关于 hf-mirror.com：** 实测对 mlx-community/* 仓库会 308 重定向回 huggingface.co（镜像没缓存），**镜像通常无用**，直接 aria2c 命中 CDN 反而最快。

### 3️⃣ 验证模型能加载

```bash
source ~/.hermes/hermes-agent/venv/bin/activate
python3 -c "
from mlx_vlm import load
model, processor = load('$HOME/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit')
print('✅ 模型加载成功')
"
```

### 4️⃣ 写 launchd plist 实现开机自启

参见 `templates/com.hermes.mlx-vision.plist`，写到 `~/Library/LaunchAgents/com.hermes.mlx-vision.plist`。

**关键设计：**
- `KeepAlive` + `Crashed: true`：进程崩了 30s 自动重启
- `RunAtLoad: true`：开机自启
- `ThrottleInterval: 30`：避免崩溃重启风暴
- 日志到 `~/.hermes/logs/mlx-vision.{log,err}`

### 5️⃣ 注册 launchd（⚠️ 必须用户在外部终端跑）

**关键陷阱：Hermes Gateway safety 机制会拦截 agent 在 chat 内执行 launchctl 命令**（检测到会影响 gateway 自身或子进程）。

**必须让用户复制下面这行到他的终端窗口手动跑：**

```bash
kill $(lsof -tiTCP:8080 -sTCP:LISTEN) 2>/dev/null
sleep 3
launchctl unload ~/Library/LaunchAgents/com.hermes.mlx-vision.plist 2>/dev/null
launchctl load ~/Library/LaunchAgents/com.hermes.mlx-vision.plist
sleep 8
launchctl list | grep mlx-vision
lsof -iTCP:8080 -sTCP:LISTEN
curl -s http://127.0.0.1:8080/v1/models
```

### 6️⃣ 改 Hermes 配置切到本地 MLX

```bash
hermes config set auxiliary.vision.base_url "http://127.0.0.1:8080/v1"
hermes config set auxiliary.vision.model "/Users/$USER/.lmstudio/models/mlx-community/Qwen3-VL-8B-Instruct-6bit"
hermes config set auxiliary.vision.api_key "not-needed"
```

⚠️ **不要直接改 ~/.hermes/config.yaml**——agent 写入会被 safety 拦截，必须用 `hermes config set`。

### 7️⃣ 端到端测试

调用 `vision_analyze` 工具发图，如果返回中文详细描述（不是 Connection error），即成功 🎉

---

## 日常运维

| 操作 | 命令 |
|---|---|
| 看服务状态 | `launchctl list \| grep mlx-vision` |
| 手动重启 | `launchctl kickstart -k gui/$(id -u)/com.hermes.mlx-vision` |
| 看实时日志 | `tail -f ~/.hermes/logs/mlx-vision.err` |
| 暂停服务 | `launchctl unload ~/Library/LaunchAgents/com.hermes.mlx-vision.plist` |
| 启用服务 | `launchctl load ~/Library/LaunchAgents/com.hermes.mlx-vision.plist` |
| 查看端口占用 | `lsof -iTCP:8080 -sTCP:LISTEN` |

---

## 🚨 已知坑

### 坑 1：HF 下载半夜卡死
hf-cli 的 xet 协议在境内"进程活着但 TCP CLOSED 5 小时不动"。**对策：用 aria2c + `--lowest-speed-limit=100K`**。

### 坑 2：hf-mirror.com 对 mlx-community 无效
会 308 重定向回主站。**对策：直接走主站 CDN**。

### 坑 3：模型偶尔编造细节
Qwen3-VL 会"看到"期望存在的东西（如把椅子边缘说成"棕色泰迪熊"）。**对策：问 OCR/具体文字识别准确率高，纯外形判断要存疑**。

### 坑 4：Gateway 拦截 launchctl
agent 在 chat 内 `launchctl load/unload/kill` 会被 safety 拦截。**对策：让用户在外部终端跑**。

### 坑 5：端口冲突
旧 mlx_vlm.server 占着 8080，launchd 无法 bind。**对策：注册前先 `kill $(lsof -tiTCP:8080 -sTCP:LISTEN)`**。

### 坑 6：venv 装错
必须 `~/.hermes/hermes-agent/venv/`，不是项目 dev venv。

### 坑 7：模型路径
`hermes config set ... model` 用绝对路径，不能用 `~`。

---

## 切换/升级模型

1. step 2 流程下新模型到 `~/.lmstudio/models/mlx-community/<新模型名>/`
2. 改 plist 里的 `--model` 路径 + `hermes config set auxiliary.vision.model <新路径>`
3. 用户跑：`launchctl kickstart -k gui/$(id -u)/com.hermes.mlx-vision`
