---
name: hermes-vision-model-setup
description: Configure Hermes' dedicated `auxiliary.vision` field to use a custom OpenAI-compatible endpoint (volcengine Ark, OpenRouter, OpenAI, etc.) for image understanding. Covers the verified config schema, the Ark Agent Plan vs Standard API key distinction (vision is NOT in Agent Plan — live-tested 401/404 June 2026), the model matrix, and a verified starter config.
type: reference
---

# Hermes Custom Vision Model Setup

Hermes has a **dedicated `auxiliary.vision:` field** in `~/.hermes/config.yaml`,
completely separate from chat models. It is used by tools that need image
understanding — `vision_analyze`, `browser_vision` (fallback path), and any
tool that calls an LLM with an image attached.

## Config Schema (verified June 2026)

The schema lives under `auxiliary.vision.*`, NOT a top-level `vision:` block:

```yaml
auxiliary:
  vision:
    provider: custom          # 'custom' for custom_providers, or a built-in name (openai, openrouter, …)
    model: doubao-seed-1-6-vision-250815
    base_url: https://ark.cn-beijing.volces.com/api/v3
    api_key: <literal-key>    # CRITICAL: literal value, NOT env var name
    timeout: 120
    extra_body: {}            # pass-through to API
    download_timeout: 30
```

Other auxiliary sections in the same file follow the same pattern:
`auxiliary.compression.*`, `auxiliary.web_extract.*`, `auxiliary.curator.*`,
etc. — all share the `(provider, model, base_url, api_key, …)` shape.

**How to set values** — direct file edits are blocked by the Hermes
security policy. Use `hermes config set`:

```bash
hermes config set auxiliary.vision.provider custom
hermes config set auxiliary.vision.model doubao-seed-1-6-vision-250815
hermes config set auxiliary.vision.base_url https://ark.cn-beijing.volces.com/api/v3
hermes config set auxiliary.vision.api_key "ark-XXXXX..."
```

Each `set` is a single value. For complex multi-field sections, call `set`
once per field. Verify afterwards with `grep -A 8 '^auxiliary:' ~/.hermes/config.yaml`.

## ⚠️ Agent Plan vs Standard API Key — Live-Tested Result (June 2026)

**Critical finding:** the user's ARK `ark-2281c7...17` key is an
**Agent Plan subscription key**. It supports the DeepSeek V4 text Agent
chain on `/api/plan/v3`, but:

| Endpoint | Result for vision models |
|---|---|
| `POST /api/plan/v3/chat/completions` (Agent Plan) | **404 `UnsupportedModel`** for every vision model tested |
| `POST /api/v3/chat/completions` (Standard inference) | **401 `AuthenticationError`** — key lacks standard inference permission |

Vision models verified failing on the Agent Plan key:
- `doubao-seed-1-6-vision-250815`
- `doubao-1-5-vision-pro-32k-250115`
- `doubao-seed-1-6-250615` (multimodal text model)

**Conclusion:** Agent Plan subscriptions and standard ARK inference
subscriptions use **different API keys with disjoint permissions**. To use
Ark vision models, create a separate API key under the "在线推理 / standard
inference" section in the ARK console, and use it in `auxiliary.vision.api_key`
with `base_url: https://ark.cn-beijing.volces.com/api/v3`.

**Quick key-validity check** before configuring (200 = valid key):

```bash
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer *** \
  https://ark.cn-beijing.volces.com/api/v3/models
```

## Volcengine Ark — Vision Model Matrix (verified model list June 2026)

Source: https://www.volcengine.com/docs/82379/1330310 (browser-scraped, model
list). All these models support image input on the standard `/api/v3` endpoint
with a standard inference key.

### Tier 1 — Dedicated vision models (best for image understanding)

| Model ID | Context | Special capabilities |
|---|---|---|
| `doubao-seed-1-6-vision-250815` | 256k | **GUI 任务处理** + 视觉定位 — the only model with native GUI agent capability |
| `doubao-1-5-vision-pro-32k-250115` | 32k | Older pure-vision, cheap and stable |

### Tier 2 — Doubao Seed 2.0 (multimodal, latest gen)

All support `多模态理解` (multimodal understanding) + visual reasoning:

- `doubao-seed-2-0-pro-260215` — flagship (256k)
- `doubao-seed-2-0-mini-260428` — value (256k)
- `doubao-seed-2-0-lite-260428` — entry (256k)
- `doubao-seed-2-0-mini-260215` — (256k, +视觉定位)
- `doubao-seed-2-0-lite-260215` — (256k, +视觉定位)
- `doubao-seed-2-0-code-preview-260215` — coding-enhanced (256k)
- `doubao-seed-1-8-251228` — previous flagship (256k, +视觉定位)

### Tier 3 — Flash series (cheapest, still multimodal)

- `doubao-seed-1-6-flash-250828` — (256k, +视觉定位)
- `doubao-seed-1-6-flash-250615` — (256k, +视觉定位)
- `doubao-seed-code-preview-251028` — (256k, +视觉定位)
- `doubao-seed-1-6-251015` — (256k, +视觉定位)
- `doubao-seed-1-6-250615` — (256k, +视觉定位)

### Pure text models (NOT vision — will reject images)

- `deepseek-v4-pro-260425`, `deepseek-v4-flash-260425`, `deepseek-v3-2-251201`
- `glm-4-7-251222`
- `doubao-1-5-pro-32k-*` (non-vision variants)

## OpenRouter Free Vision Models (Alternative to Ark)

When the user's Ark key is Agent Plan only (vision NOT supported), OpenRouter provides free vision-capable models that work with the existing `OPENROUTER_API_KEY`. These are the free-tier vision models discovered June 2026:

| Model ID | Modality | Notes |
|---|---|---|
| `google/gemma-4-31b-it:free` | text+image+video→text | ⭐ Best general-purpose free vision — strong reasoning, 1M context |
| `google/gemma-4-26b-a4b-it:free` | text+image+video→text | Lighter variant of Gemma 4 |
| `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` | text+image+audio+video→text | Omni-modal — also handles audio+video |
| `nvidia/nemotron-nano-12b-v2-vl:free` | text+image+video→text | Lightweight VL model |
| `nex-agi/nex-n2-pro:free` | text+image→text | |
| `nvidia/nemotron-3.5-content-safety:free` | text+image→text | Content safety focused |

### OpenRouter Config

```yaml
auxiliary:
  vision:
    provider: openrouter          # Uses existing OPENROUTER_API_KEY
    model: google/gemma-4-31b-it:free
    base_url: ''                  # MUST be empty — built-in provider uses its own URL
    api_key: ''                   # MUST be empty — built-in provider reads OPENROUTER_API_KEY
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

**⚠️ CRITICAL:** When switching from `custom` (Ark) to `openrouter`, the old `base_url` and `api_key` values remain in config.yaml. These stale values **override** the built-in provider's defaults — the agent will still send requests to the old Ark endpoint with the old Ark key. **Always explicitly clear them:**

```bash
hermes config set auxiliary.vision.base_url ''
hermes config set auxiliary.vision.api_key ''
```

Then verify with `grep -A 8 '^auxiliary:' ~/.hermes/config.yaml` — both should show empty strings.

**Session restart required** — `vision_analyze` caches the old config. Run `/reset` in Hermes after changing vision config.

### Live-tested: OpenRouter free vision with Gemma 4

In this session (June 11, 2026), the user's Ark Agent Plan key was confirmed to NOT support vision models (404 on Plan API, 401 on Standard API). The vision provider was switched to OpenRouter's free `google/gemma-4-31b-it:free` model.

**Switching pattern (custom → openrouter):**

```bash
hermes config set auxiliary.vision.provider openrouter
hermes config set auxiliary.vision.model google/gemma-4-31b-it:free
hermes config set auxiliary.vision.base_url ''    # ← CRITICAL: clear stale values
hermes config set auxiliary.vision.api_key ''      # ← CRITICAL: clear stale values
hermes config set auxiliary.vision.timeout 120
```

The `base_url` and `api_key` clear steps are **not optional** — without them, the old Ark endpoint/key persist and override the built-in OpenRouter provider's defaults. Even after setting `provider: openrouter`, the agent still sends requests to `https://ark.cn-beijing.volces.com/api/v3` with the old Ark key.

**Verification after switch:** `grep -A 8 '^auxiliary:' ~/.hermes/config.yaml` should show:
- `provider: openrouter`
- `model: google/gemma-4-31b-it:free`
- `base_url: ''`
- `api_key: ''`

**Known issue:** even with correct config, the running session caches the old vision config. `vision_analyze` returns 400 "doubao-seed-1-6-vision-250815 is not a valid model ID" because it's still using the old model name against the old endpoint. The fix is always `/reset` (session restart).

## Recommended Starter Config

For most users who want good vision + reasonable cost:

```yaml
auxiliary:
  vision:
    provider: custom
    model: doubao-seed-1-6-vision-250815     # GUI-aware vision
    base_url: https://ark.cn-beijing.volces.com/api/v3
    api_key: <your-standard-inference-key>   # NOT the Agent Plan key
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

Note: `auxiliary.vision` has no `fallbacks` field in the current schema —
only a single `model` per section. For multi-model fallbacks, configure
multiple auxiliary sections OR use a single robust model (e.g.
`doubao-seed-1-6-vision-250815` which handles most cases).

## Verifying the Vision Model Is Reachable

Quickest live test — POST an image URL to the chat completions endpoint:

```python
import requests
KEY = "ark-XXXXX..."   # your standard inference key
r = requests.post(
    "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
    headers={"Content-Type": "application/json",
             "Authorization": f"Bearer {KEY}"},
    json={
        "model": "doubao-seed-1-6-vision-250815",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": "describe this image briefly"},
            {"type": "image_url", "image_url": {"url": "https://example.com/test.jpg"}}
        ]}],
        "max_tokens": 100,
    },
    timeout=30,
)
print(r.status_code, r.text[:300])
```

If this returns 200 with a description, vision will work in Hermes.

## Pitfalls

1. **Agent Plan ≠ vision-capable** — the most common mistake. Agent Plan
   keys return 404 for ALL vision models. You need a standard inference key
   from the ARK console. See the live-test table above.

2. **`api_key` is taken literally** — same as the chat-side custom
   provider pitfall. Setting `api_key: ARK_API_KEY` sends the literal
   string `"ARK_API_KEY"` as the bearer token. Put the actual key value
   directly. (This rule applies to `auxiliary.vision` as well as
   `custom_providers` — both fields bypass env var resolution.)

3. **`hermes config set` is the only way to modify config.yaml** — direct
   `write_file` / `patch` / `sed` are all blocked by Hermes security
   policy. Always use `hermes config set <key.path> <value>` for individual
   values. After all sets, verify with `grep`.

4. **Pure text models silently reject images** with a 400 or empty
   `choices`. If `vision_analyze` returns nothing, check that the model
   actually supports `多模态理解` per the matrix above — `deepseek-v4-pro`
   is a common wrong pick.

5. **`max_tokens` matters for vision models.** Some models (esp. older
   `doubao-1-5-vision`) need `max_tokens >= 50` or they output whitespace.
   The vision tool usually sets this, but custom probes should follow.

6. **Model IDs are case-sensitive.** `doubao-seed-1-6-vision-250815` works;
   `Doubao-Seed-1-6-Vision-250815` returns 404.

7. **Image input format is OpenAI-style** — `image_url` content blocks
   in the `messages` array. Hermes' vision tools convert images to this
   format automatically. The models above all accept the standard
   `image_url` schema.

8. **`vision_analyze` URL validation** — the tool rejects some image
   sources with "Invalid image source" before even calling the API. If
   you see this error, the URL may need to be downloaded to a local file
   first. Download with `curl -sLo /tmp/img.png "$URL"` and pass the local
   path. (Hermes' vision tool is stricter about URLs than the underlying
   API; this is a tool quirk, not a model issue.)

## Verification

After writing the config:

1. Run `hermes config set` for each field, then `grep -A 8 '^auxiliary:' ~/.hermes/config.yaml` to confirm.
2. Run the Python probe above against your key — must return 200.
3. Restart the gateway (or run `/reset` in-session) so vision picks up the new field.
4. Send any image to the bot and ask "描述一下这张图" — if it returns a description, vision is working.
5. Check `~/.hermes/logs/agent.log` for any `vision` / `multimodal` errors on the first call.

## LM Studio Local Vision (macOS)

When cloud vision models are rate-limited (OpenRouter free tier: 50/day) or unavailable (Ark Agent Plan lacks vision), **LM Studio on macOS** provides a zero-cost local alternative using Gemma 4's built-in vision projection file.

### Prerequisites

- LM Studio installed (`/Applications/LM Studio.app`)
- `lms` CLI available at `~/.lmstudio/bin/lms`
- A GGUF model with a companion `mmproj-*.gguf` vision projection file in the same directory

### Known Working Setup (verified June 2026)

| Component | Value |
|-----------|-------|
| Model | `gemma-4-12b-it-Q6_K.gguf` (9.28 GiB) |
| Vision proj | `mmproj-BF16.gguf` (167 MiB) |
| Model dir | `~/.lmstudio/models/unsloth/gemma-4-12b/` |
| API port | `http://127.0.0.1:1234/v1` |

### Setup Steps

```bash
# 1. Start the API server
~/.lmstudio/bin/lms server start
# → "Success! Server is now running on port 1234"

# 2. Load the model (interactive — pipe the name)
echo "gemma-4-12b" | ~/.lmstudio/bin/lms load
# → "Model loaded successfully in 13.27s."

# 3. Verify the model is available
curl -s http://127.0.0.1:1234/v1/models
# → {"data":[{"id":"gemma-4-12b",...}]}

# 4. Test vision with a local image
python3 -c "
import base64, json, urllib.request
with open('/tmp/img_small.jpg', 'rb') as f:
    b64 = base64.b64encode(f.read()).decode()
payload = {
    'model': 'gemma-4-12b',
    'messages': [{
        'role': 'user',
        'content': [
            {'type': 'text', 'text': 'Describe this image in Chinese.'},
            {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{b64}'}}
        ]
    }],
    'max_tokens': 2048
}
req = urllib.request.Request(
    'http://127.0.0.1:1234/v1/chat/completions',
    data=json.dumps(payload).encode(),
    headers={'Content-Type': 'application/json'}
)
with urllib.request.urlopen(req, timeout=120) as resp:
    data = json.loads(resp.read())
    print(data['choices'][0]['message']['content'])
"
```

### Hermes Config

```yaml
auxiliary:
  vision:
    provider: lmstudio
    model: gemma-4-12b
    base_url: http://127.0.0.1:1234/v1
    api_key: ''                # LM Studio doesn't require auth
    timeout: 120
    extra_body: {}
    download_timeout: 30
```

Apply via `hermes config set`:

```bash
hermes config set auxiliary.vision.provider lmstudio
hermes config set auxiliary.vision.model gemma-4-12b
hermes config set auxiliary.vision.base_url "http://127.0.0.1:1234/v1"
hermes config set auxiliary.vision.api_key ''
```

### ⚠️ Known Limitation (Corrected June 2026): Stale `base_url`/`api_key` Override, Not Main Provider

**Previously documented as:** `vision_analyze` always uses the main provider, ignoring `auxiliary.vision`.

**Live-tested correction (June 12, 2026):** `vision_analyze` **DOES** use `auxiliary.vision` when configured correctly. The earlier failures were caused by **stale `base_url` and `api_key` values** (pitfall #13), not by the tool ignoring the auxiliary config.

The sequence that proved this:
1. `auxiliary.vision` was set to `provider: openrouter` with stale `base_url: https://ark.cn-beijing.volces.com/api/v3` and `api_key: <ark-key>` → `vision_analyze` failed (404 UnsupportedModel from Ark)
2. After clearing `base_url` and `api_key` (empty strings), `vision_analyze` still failed because the running session cached the old config
3. After switching to `provider: lmstudio` with `base_url: http://127.0.0.1:1234/v1` and `api_key: ''`, `vision_analyze` **succeeded** — returning a proper description of an anime-style image

**Root cause of the confusion:** When `provider` is set to a built-in name (openrouter, openai, etc.) but `base_url`/`api_key` are non-empty, the tool uses the explicit `base_url`/`api_key` values, NOT the built-in provider's defaults. This makes it look like the tool is "ignoring" the provider setting when really it's following the stale explicit values.

**Correct understanding:**
- `vision_analyze` reads `auxiliary.vision.*` fields directly
- If `base_url` is non-empty, it uses that URL regardless of `provider`
- If `api_key` is non-empty, it uses that key regardless of `provider`
- Only when both are empty does the built-in provider's default endpoint/key activate
- **Session restart (`/reset`) is still required** for config changes to take effect in the running session

### Pitfalls

1. **`lms load` is interactive** — piping `echo "model-name"` works but may need the exact model identifier from `lms ls`.
2. **Large images timeout** — gemma-4-12b on Apple Silicon handles ~400px images in ~30s. 1200px+ images can take 2+ minutes. Pre-resize with `sips -Z 400` before sending.
3. **Model must be loaded before each use** — if LM Studio unloads the model (e.g. after closing the GUI), re-run `lms load gemma-4-12b`.
4. **`lms server start` is idempotent** — running it when the server is already up prints "Success!" again with no side effects.
5. **MMProj file required** — without `mmproj-BF16.gguf` (or equivalent) in the model directory, LM Studio loads the model as text-only. Vision requests return 400 "model does not support image input".

## Reference

- Ark model list: https://www.volcengine.com/docs/82379/1330310
- Ark Agent Plan key 404 error: `UnsupportedModel` — see the live-test table above
- Hermes config field name and schema: `~/.hermes/config.yaml` (`auxiliary.vision.*` block)
- Custom provider setup: see main `model-fallback` SKILL.md → "Custom (Named) Providers"
- `custom-provider-ark-quickstart.md` — Volcano Engine Ark setup walkthrough
