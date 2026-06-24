# cc-switch Provider Setup Guide

cc-switch (Codex++) manages third-party providers for Codex CLI via a local proxy architecture. This reference covers adding, switching, and troubleshooting providers.

## Architecture

```
Codex CLI → Codex++ (127.0.0.1:57321) → cc-switch (127.0.0.1:15721) → Provider API
```

- **Codex++** runs on port 57321 — intercepts Codex's API calls
- **cc-switch** runs on port 15721 — translates Responses API ↔ Chat API, manages providers
- **Codex config.toml** at `~/.codex/config.toml` points `[model_providers.custom].base_url` at the Codex++ proxy

## Database Location

`~/.cc-switch/cc-switch.db` (SQLite)

## Tables

### `providers` table

| Column | Type | Description |
|--------|------|-------------|
| id | TEXT | UUID |
| app_type | TEXT | `"codex"`, `"claude"`, or `"gemini"` |
| name | TEXT | Display name |
| settings_config | TEXT | JSON: auth, config, modelCatalog |
| website_url | TEXT | Provider website |
| category | TEXT | e.g. `"cn_official"` |
| created_at | INTEGER | Unix ms timestamp |
| sort_index | INTEGER | Display order |
| notes | TEXT | Description |
| icon | TEXT | Icon name |
| icon_color | TEXT | Hex color |
| meta | TEXT | JSON: apiFormat, codexChatReasoning |
| is_current | BOOLEAN | 1 = active |
| in_failover_queue | BOOLEAN | 1 = in failover |
| cost_multiplier | TEXT | e.g. `"1.0"` |
| provider_type | TEXT | e.g. `"ark"`, `"deepseek"` |

### `provider_endpoints` table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Auto-increment |
| provider_id | TEXT | FK to providers.id |
| app_type | TEXT | `"codex"` |
| url | TEXT | API base URL |
| added_at | INTEGER | Unix ms timestamp |

### `proxy_config` table

Controls proxy behavior per app_type. Key fields:
- `host`/`port`: proxy listen address (default `127.0.0.1:15721`)
- `response_mode`: `"response"` (Responses API) or `"chat"` (Chat API)

## Adding a New Provider

### 1. Generate provider UUID

```python
import uuid
print(str(uuid.uuid4()))
```

### 2. Build settings_config JSON

```json
{
  "auth": {
    "OPENAI_API_KEY": "<your-api-key>"
  },
  "config": "model_provider = \"custom\"\nmodel = \"<default-model>\"\ndisable_response_storage = true\n\n[model_providers]\n[model_providers.custom]\nname = \"<provider-name>\"\nbase_url = \"<api-base-url>\"\nwire_api = \"responses\"\nrequires_openai_auth = true\n",
  "modelCatalog": {
    "models": [
      {"model": "<model-id>", "displayName": "<Display Name>", "contextWindow": 1000000}
    ]
  }
}
```

### 3. Build meta JSON

```json
{
  "commonConfigEnabled": true,
  "endpointAutoSelect": true,
  "apiFormat": "openai_chat",
  "codexChatReasoning": {
    "supportsThinking": true,
    "supportsEffort": true,
    "thinkingParam": "thinking",
    "effortParam": "reasoning_effort",
    "effortValueMode": "deepseek",
    "outputFormat": "reasoning_content"
  }
}
```

### 4. Insert into database

```python
import sqlite3, json

db = sqlite3.connect("/Users/jushuai/.cc-switch/cc-switch.db")
cur = db.cursor()

cur.execute("""
    INSERT OR REPLACE INTO providers 
    (id, app_type, name, settings_config, website_url, category, created_at, sort_index, 
     notes, icon, icon_color, meta, is_current, in_failover_queue, cost_multiplier, provider_type)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    provider_id, "codex", "Provider Name",
    json.dumps(settings_config),
    "https://example.com",
    "cn_official", now, 2,
    "Description",
    "icon-name", "#HEXCOLOR",
    json.dumps(meta),
    0, 0, "1.0", "provider-type"
))

cur.execute("""
    INSERT OR REPLACE INTO provider_endpoints
    (id, provider_id, app_type, url, added_at)
    VALUES (?, ?, ?, ?, ?)
""", (int(time.time()), provider_id, "codex", "https://api.example.com/v1", now))

db.commit()
```

### 5. Switch to the new provider

```python
# Unset current
cur.execute("UPDATE providers SET is_current=0, in_failover_queue=0 WHERE app_type='codex' AND is_current=1")
# Set new provider
cur.execute("UPDATE providers SET is_current=1, in_failover_queue=1 WHERE id=?", (new_provider_id,))
db.commit()
```

### 6. Restart cc-switch

```bash
# Find PID
ps aux | grep "cc-switch" | grep -v grep
# Kill and restart
kill <PID>
open -a "CC Switch"
```

## Verification

### Test cc-switch proxy directly

```bash
curl -sk "http://127.0.0.1:15721/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"hi"}],"max_tokens":20}'
```

### Test Codex++ proxy (full chain)

```bash
curl -sk "http://127.0.0.1:57321/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model-id>","messages":[{"role":"user","content":"hi"}],"max_tokens":20}'
```

### Check provider status

```bash
sqlite3 ~/.cc-switch/cc-switch.db "SELECT name, is_current, in_failover_queue FROM providers WHERE app_type='codex';"
```

## Example: Adding Ark (火山方舟)

See the session that produced this guide for the full working example. Key values:

- **Base URL**: `https://ark.cn-beijing.volces.com/api/plan/v3`
- **API format**: OpenAI Chat API compatible
- **Models**: `deepseek-v4-flash`, `deepseek-v4-pro`, `deepseek-r1`, `minimax-chat`, `glm-4`
- **Provider type**: `"ark"`
- **Icon color**: `#FF6A00`
