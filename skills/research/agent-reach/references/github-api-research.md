# GitHub API 深度调研

当 `web_extract`/`browser` 被 GitHub 屏蔽或需要结构化数据时，直接用 GitHub REST API。

## 链路选择

```
web_extract(gh URL) → blocked? → GitHub API (api.github.com)
browser(gh URL) → flaky/slow? → GitHub API
GitHub API → blocked? → browser 兜底
```

## 常用 API 端点

```bash
# 仓库元信息（星标、fork、许可证、描述、活跃度）
curl -sL "https://api.github.com/repos/owner/repo"

# 顶层文件列表
curl -sL "https://api.github.com/repos/owner/repo/contents/"

# 子目录文件列表
curl -sL "https://api.github.com/repos/owner/repo/contents/path/to/dir"

# 读取文件内容（返回 base64 编码的 content 字段）
curl -sL "https://api.github.com/repos/owner/repo/contents/README.md"

# README（自动定位）
curl -sL "https://api.github.com/repos/owner/repo/readme"

# 完整目录树（递归，适合大仓库快速了解结构）
curl -sL "https://api.github.com/repos/owner/repo/git/trees/main?recursive=1"
```

## Python 解码单文件

```bash
curl -sL "https://api.github.com/repos/owner/repo/contents/README.md" \
  | python3 -c "import sys,json,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

## 目录树分析（获取类别/技能数量统计）

```bash
curl -sL "https://api.github.com/repos/owner/repo/git/trees/main?recursive=1" \
  | python3 -c "
import sys,json
data = json.load(sys.stdin)
dirs = set()
for t in data['tree']:
    if t['type'] == 'tree' and t['path'].startswith('prefix/'):
        parts = t['path'].split('/')
        if len(parts) >= 3:
            dirs.add(parts[2])
print(f'Subdir count: {len(dirs)}')
for d in sorted(dirs):
    print(f'  {d}')
"
```

## 调研工作流

1. **获取元信息** — `GET /repos/owner/repo` → 星标、fork、许可证、语言、描述、创建日期
2. **读 README** — `GET /repos/owner/repo/readme` → 项目介绍、安装说明
3. **看文件结构** — `GET /repos/owner/repo/contents/` → 顶层布局
4. **读关键文档** — AGENTS.md / CLAUDE.md / CONTRIBUTING.md / 特定重要文件
5. **浏览目录树** — `GET /repos/owner/repo/git/trees/main?recursive=1` → 全量结构，用于统计类别/数量/规模
6. **浏览器兜底** — 当需要视觉内容（截图、页面交互）时回退到 browser_navigate

## 注意

- 未认证的 API 有请求频率限制（60 req/hr 按 IP）。高频场景加 `Authorization: token $GH_TOKEN`。
- `raw.githubusercontent.com` 的 raw 文件比 API 返回更快，但可能会被 web_extract 屏蔽，此时用 API 的 base64 解码方式。
- 仓库文件超过 1MB 时 `/contents/` 端点返回 `{"message": "This API returns blobs up to 1 MB in size"}`，改用 `git/blobs/` 端点。
