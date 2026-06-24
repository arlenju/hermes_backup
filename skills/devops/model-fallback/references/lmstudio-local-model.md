# LM Studio 本地模型管理

## 模型文件存放

LM Studio 从 `~/.lmstudio/models/` 下自动发现模型，按 `owner/model-name/filename.gguf` 结构组织：

```
~/.lmstudio/models/
├── unsloth/gemma-4-12b/
│   ├── gemma-4-12b-it-Q6_K.gguf
│   └── mmproj-BF16.gguf
└── yuxinlu1/gemma-4-12B-coder-fable5-composer2.5-v1-GGUF/
    └── gemma4-coding-Q6_K.gguf
```

## CLI 管理（`lms`）

LM Studio 自带 `~/.lmstudio/bin/lms` CLI：

```bash
# 列出已安装模型
~/.lmstudio/bin/lms ls

# 导入 GGUF 文件
~/.lmstudio/bin/lms import /path/to/model.gguf

# 加载模型到内存（GPU 全量加速）
~/.lmstudio/bin/lms load <model-key> --gpu max --context-length 32768

# 查看已加载模型
~/.lmstudio/bin/lms ps

# 卸载模型
~/.lmstudio/bin/lms unload <model-key>

# 启动 OpenAI 兼容 API 服务（默认端口 1234）
~/.lmstudio/bin/lms server start

# 停止 API 服务
~/.lmstudio/bin/lms server stop

# 查看 API 服务状态
~/.lmstudio/bin/lms server status
```

## 关键区别

| 概念 | 说明 |
|------|------|
| `lms load` | 将模型加载到 GPU 内存，仅本地可用 |
| `lms server start` | 启动 OpenAI 兼容 API 服务（端口 1234），外部可调用 |
| LM Studio GUI 端口 41343 | 仅限 GUI 内部通信，不提供 OpenAI API |

**必须先 `lms load` 加载模型，再 `lms server start` 启动 API 服务。**

## 测试 API

```bash
curl -s http://127.0.0.1:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "<model-key>", "messages": [{"role": "user", "content": "1+1="}], "max_tokens": 10}'
```

## Hermes 配置

```yaml
# ~/.hermes/config.yaml
model:
  provider: lmstudio
  default: <model-key>
  base_url: http://127.0.0.1:1234/v1
  api_key: lmstudio  # 任意非空字符串即可
```

切换命令：
```bash
hermes config set model.provider lmstudio
hermes config set model.default <model-key>
```

需要 `/reset` 新会话生效。

## 下载 GGUF 模型（国内加速）

见 `agent-reach` skill 的 `references/hf-mirror-download.md`。
