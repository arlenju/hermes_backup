# Session: Model Health Testing (2026-06-07)

Tested 7 models on OpenRouter for fallback readiness. Results:

## Environment
- Hermes profile: default
- Provider: deepseek (primary, ran out of credits — HTTP 402)
- OpenRouter key: stored in `~/.hermes/.env` as `OPENROUTER_API_KEY`
- Script: `~/.hermes/scripts/model_health.py`

## Test Results

| Model | Latency | Status | Notes |
|-------|---------|--------|-------|
| Google Gemma 4 31B | 1.7s | ✅ | Fastest free model |
| NVIDIA Nemotron Ultra 550B | 5.2s | ✅ | Large model, decent speed |
| NVIDIA Nemotron Super 120B | 7.1s | ✅ | Cheaper variant |
| Nous Hermes 3 405B | ~5s (retry) | ✅ | Worked on retry |
| Moonshot Kimi K2.6 | — | ❌ 429 | Rate limited |
| Qwen3 Coder | — | ❌ 429 | Rate limited |
| DeepSeek V4 Flash | — | ❌ 402 | Insufficient balance |

## Key Takeaways

1. Google Gemma 4 31B is the fastest free fallback on OpenRouter (~1.7s)
2. Free models have shared rate limits — expect occasional 429s, retry after 5s
3. DeepSeek direct API may run out of credits without warning (HTTP 402)
4. Fallback chain with 5+ layers ensures Hermes stays online
5. Hourly health check + 6-hourly reorder cron jobs keep the chain optimal

## Cron Jobs Created

- `model_health.py` (hourly): reports speed table
- `model_health.py reorder` (6-hourly): tests + re-sorts fallback_providers
