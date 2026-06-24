# HuggingFace 模型下载（国内镜像 + 多线程加速）

当直连 HuggingFace 超时或极慢时（国内常见），使用 hf-mirror.com 镜像 + aria2 多线程下载。

## 场景

下载 GGUF 模型到本地 LM Studio，直连 HF 卡死（`Operation timed out`）。

## 方案

### 1. 使用 Motrix（aria2 GUI）通过 RPC 控制

```bash
# Motrix 启动后 aria2 RPC 在 16800 端口
# 添加下载任务（16 连接并行）
curl -s http://localhost:16800/jsonrpc -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "aria2.addUri",
  "params":[["https://hf-mirror.com/<owner>/<repo>/resolve/main/<filename>.gguf"],
    {"dir": "/path/to/save",
     "out": "<filename>.gguf",
     "split": "16",
     "max-connection-per-server": "16",
     "continue": "true"}]
}'
```

### 2. 查看下载进度

```bash
curl -s http://localhost:16800/jsonrpc -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "aria2.tellStatus",
  "params":["<gid>"]
}' | python3 -c "
import json,sys
d = json.load(sys.stdin)['result']
total = int(d['totalLength'])
completed = int(d['completedLength'])
speed = int(d['downloadSpeed'])
pct = completed/total*100 if total > 0 else 0
print(f'{total/1024/1024/1024:.2f} GB | {completed/1024/1024:.0f} MB ({pct:.1f}%) | {speed/1024/1024:.1f} MB/s')
"
```

### 3. 取消任务

```bash
curl -s http://localhost:16800/jsonrpc -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "aria2.remove",
  "params":["<gid>"]
}'
```

## 关键点

- **URL 替换**：`huggingface.co` → `hf-mirror.com`，路径不变
- **多线程**：`split=16, max-connection-per-server=16`，实测国内可达 139 MB/s
- **断点续传**：`continue=true`，中断后重跑自动续传
- **Motrix 路径**：`/Applications/Motrix.app`，启动后 aria2 自动在 16800 端口监听
- **aria2 直连**：也可 `brew install aria2` 后直接命令行使用，不依赖 Motrix GUI
