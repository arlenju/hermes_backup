# 国内下载 HuggingFace 模型：镜像站方案

在中国大陆直连 huggingface.co 经常超时/断连。使用 **hf-mirror.com** 镜像站可以稳定满速下载。

## aria2 / Motrix 多线程下载

### 通过 Motrix（aria2 GUI）RPC 接口

```bash
# Motrix 默认 RPC 端口 16800
# 添加下载任务
curl -s http://localhost:16800/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "aria2.addUri",
    "params":[["https://hf-mirror.com/<user>/<repo>/resolve/main/<file>"], 
      {"dir": "/path/to/save",
       "out": "<filename>",
       "split": "16",
       "max-connection-per-server": "16",
       "continue": "true"}]
  }'
```

### 关键参数
| 参数 | 值 | 说明 |
|------|-----|------|
| `split` | 16 | 分16块下载 |
| `max-connection-per-server` | 16 | 每服务器16连接 |
| `continue` | true | 支持断点续传 |

### 查看下载进度
```bash
curl -s http://localhost:16800/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "aria2.tellActive",
    "params":[]
  }' | python3 -c "
import json,sys
d = json.load(sys.stdin)
for task in d.get('result', []):
    total = int(task['totalLength'])
    completed = int(task['completedLength'])
    speed = int(task['downloadSpeed'])
    print(f'{(completed/total*100):.0f}% | {completed/1024/1024:.0f}/{total/1024/1024:.0f} MB | {speed/1024/1024:.1f} MB/s')
"
```

### 查看指定任务进度
```bash
curl -s http://localhost:16800/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "aria2.tellStatus",
    "params":["<gid>"]
  }'
```

## HF CLI 替代方案（国内不可用时）
- `huggingface-cli` 已废弃，改用 `hf`
- `hf download` 命令在国内同样会超时
- 优先用 aria2 直接下载镜像站链接

## 常见模型下载链接格式
```
https://hf-mirror.com/<user>/<repo>/resolve/main/<filename>.gguf
```
