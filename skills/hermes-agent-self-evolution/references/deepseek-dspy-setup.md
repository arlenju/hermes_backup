# DeepSeek + DSPy 配置参考

evolution engine（DSPy + GEPA）使用 LiteLLM 作为底层 LLM 调用库，支持所有 LiteLLM provider。

## 使用 DeepSeek 作为优化器/评估器

```bash
export DEEPSEEK_API_KEY="sk-..."  # 从 ~/.hermes/.env 读取

python -m evolution.skills.evolve_skill \
  --skill <skill-name> \
  --optimizer-model deepseek/deepseek-v4-flash \
  --eval-model deepseek/deepseek-v4-flash \
  --iterations 10 \
  --eval-source synthetic
```

## 支持的 provider 前缀

| Provider | 前缀 | 示例 model ID |
|----------|------|---------------|
| DeepSeek | `deepseek/` | `deepseek/deepseek-v4-flash` |
| OpenAI | `openai/` | `openai/gpt-4.1` (默认) |
| Anthropic | `anthropic/` | `anthropic/claude-sonnet-4` |
| OpenRouter | `openrouter/` | `openrouter/anthropic/claude-sonnet-4` |
| Google | `gemini/` | `gemini/gemini-2.5-pro` |

## 环境变量

evolution engine 读取的 API key 遵循 LiteLLM 规范（`<PROVIDER>_API_KEY` 格式）：

- DeepSeek: `DEEPSEEK_API_KEY`
- OpenAI: `OPENAI_API_KEY`
- Anthropic: `ANTHROPIC_API_KEY`
- OpenRouter: `OPENROUTER_API_KEY`

## Pitfall: API Key 被 Hermes 工具截断

在 `execute_code` 中构造 API key 字符串时，如果 key 包含 GitHub PAT 或其他敏感模式，
Hermes 的工具层会自动截断（如 `github...VRMZ`）。

**解决方案：** 从 `.env` 文件直接读取，不要硬编码：

```python
import os
key = os.environ.get("DEEPSEEK_API_KEY", "")
```

或者在 shell 中通过环境变量传递：

```bash
export DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY ~/.hermes/.env | cut -d= -f2)
```
