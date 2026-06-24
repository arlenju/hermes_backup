# Model Health Monitoring — Known Issues & Quirks

The user's setup uses `~/.hermes/scripts/model_health.py` for automated fallback management:
- **Hourly**: `model_health.py` (health check only)
- **Every 6h**: `model_health.py reorder` (tests all models, re-ranks fallback_providers in config.yaml)

## Critical Quirks (as of 2026-06-07 fixes)

### 1. DeepSeek tested via OpenRouter → false 402 failures

The script tests ALL models (including DeepSeek V4 Flash) via the **OpenRouter API**, not the direct DeepSeek API. OpenRouter returns HTTP 402 ("Insufficient credits") because the user's OpenRouter account has never purchased credits there.

**Reality**: The direct DeepSeek API (`api.deepseek.com`) works fine (returns 200) via `DEEPSEEK_API_KEY` in `~/.hermes/.env`. The monitoring report looks worse than it actually is.

### 2. lmstudio moved to last position (fixed this session)

`update_fallback_order()` was patched to append lmstudio LAST as the ultimate fallback, matching user preference. Previously it was hardcoded first.

### 3. Nemotron S 120B kept at 倒数第二 when unhealthy

User decision: Nemotron S stays in the fallback list at 倒数第二 even when unhealthy (IncompleteRead). If it recovers, the next reorder cycle picks it up by speed. If still dead, it stays at 倒数第二. Rationale: give it a chance to auto-recover without blocking faster models.

### 4. Dead OpenRouter free models are NOT removed from fallback list

The `reorder` mode sorts healthy models by speed and appends them, but **never removes entries that were previously in the list** unless they're explicitly excluded. Nemotron S is the only model with special handling. Other dead models (Qwen3, Nous Hermes, Kimi) are not in the active fallback chain, so this is currently a non-issue.

### 5. Fallback reorder requires /reset to take effect

After `model_health.py reorder` writes the new `fallback_providers` to `config.yaml`, the running session doesn't pick it up until the user runs `/reset` or starts a new session.

### 6. HTTPError + IncompleteRead crash (fixed this session)

When OpenRouter returns HTTP 429 with a chunked response body, the original `except HTTPError` handler tried `e.read().decode()` which crashed with `IncompleteRead`. Fixed by wrapping `e.read()` in a nested try/except, falling back to `f"HTTP {e.code}"`.

## Reorder Logic (current)

```python
# 1. Working OpenRouter free models sorted by speed (fastest first)
# 2. Nemotron S goes to 倒数第二 if unavailable, otherwise sorted by speed
# 3. lmstudio ALWAYS last (兜底)
# 4. If ALL models fail, write only lmstudio as sole fallback
```

## Model State (as of 2026-06-07)

| Model | Via | Health | Notes |
|-------|-----|--------|-------|
| DeepSeek V4 Flash | direct | ✅ | Works, OpenRouter report is misleading |
| DeepSeek V4 Flash | OpenRouter | ❌ | HTTP 402 — insufficient OpenRouter credits |
| LM Studio gemma-4-12b | localhost:1234 | ✅ | Last兜底 (not in reorder speed test) |
| Google Gemma 4 31B | OpenRouter free | ⚠️ | OK when not rate-limited, ~1.4s |
| NVIDIA Nemotron U 550B | OpenRouter free | ⚠️ | OK when not rate-limited, ~1.8s |
| NVIDIA Nemotron S 120B | OpenRouter free | ❌ | IncompleteRead — kept at 倒数第二 per user |
| Moonshot Kimi K2.6 | OpenRouter free | ❌ | Rate limited, very slow (~22s when working) |
| Nous Hermes 3 405B | OpenRouter free | ❌ | HTTP 429 rate-limited |
| Qwen3 Coder | OpenRouter free | ❌ | HTTP 429 rate-limited |
