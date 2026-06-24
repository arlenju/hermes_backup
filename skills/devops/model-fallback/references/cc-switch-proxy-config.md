# CC Switch Proxy Configuration — Troubleshooting Guide

[CC Switch](https://github.com/saladday/cc-switch-cli) is a desktop app (Tauri 2) that manages AI coding CLI tools (Claude Code, Codex, Gemini, OpenCode, OpenClaw) by running a local proxy and intercepting their API calls to route through third-party providers.

## Architecture

```
Claude Code ──→ http://127.0.0.1:15721 ──→ CC Switch Proxy ──→ https://api.deepseek.com/anthropic/v1/messages
Codex       ──→ http://127.0.0.1:15721/v1 ──→ CC Switch Proxy ──→ https://api.deepseek.com/v1/chat/completions
```

CC Switch:
1. Sets `ANTHROPIC_BASE_URL=http://127.0.0.1:15721` in `~/.claude/settings.json` (Claude)
2. Sets `base_url=http://127.0.0.1:15721/v1` in Codex config.toml
3. Runs a local proxy on `127.0.0.1:15721`
4. The proxy translates the request format and forwards to the configured upstream provider

## Key Files

| Path | Purpose |
|------|---------|
| `/Applications/CC Switch.app` | Desktop app bundle |
| `~/.cc-switch/cc-switch.db` | SQLite database — providers, endpoints, proxy config |
| `~/.cc-switch/settings.json` | App settings (visible apps, current providers, language) |
| `~/.cc-switch/logs/cc-switch.log` | Proxy logs — request forwarding, errors |
| `~/.claude/settings.json` | Claude Code config — **managed by CC Switch** (overwritten on restart) |
| `/Applications/Codex.app/config.toml` | Codex config — **managed by CC Switch** |
| `/Applications/Codex.app/auth.json` | Codex API key file (read by Codex at startup) |

## Database Schema (cc-switch.db)

### `providers` table
```sql
CREATE TABLE providers (
    id TEXT NOT NULL,           -- UUID or "claude-official" / "codex-official"
    app_type TEXT NOT NULL,     -- "claude", "codex", "gemini", "hermes"
    name TEXT NOT NULL,         -- Display name e.g. "DeepSeek"
    settings_config TEXT NOT NULL, -- JSON: env vars, auth, model config
    website_url TEXT,
    category TEXT,              -- "official", "cn_official", "custom"
    created_at INTEGER,
    sort_index INTEGER,
    notes TEXT,
    icon TEXT,
    icon_color TEXT,
    meta TEXT NOT NULL DEFAULT '{}', -- JSON: apiFormat, commonConfigEnabled, etc.
    is_current BOOLEAN NOT NULL DEFAULT 0,
    in_failover_queue BOOLEAN NOT NULL DEFAULT 0,
    cost_multiplier TEXT NOT NULL DEFAULT '1.0',
    limit_daily_usd TEXT,
    limit_monthly_usd TEXT,
    provider_type TEXT,
    PRIMARY KEY (id, app_type)
);
```

### `provider_endpoints` table
```sql
CREATE TABLE provider_endpoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_id TEXT NOT NULL,
    app_type TEXT NOT NULL,
    url TEXT NOT NULL,           -- e.g. "https://api.deepseek.com/anthropic"
    added_at INTEGER,
    FOREIGN KEY (provider_id, app_type) REFERENCES providers(id, app_type)
);
```

### `proxy_config` table
Columns: `app_type`, `enabled`, `host`, `port`, `claude_plugin`, `codex_plugin`, `gemini_plugin`, `max_retries`, `timeout`, `connect_timeout`, `read_timeout`, `max_concurrent`, `rate_limit`, `rate_window_sec`, `retry_backoff`, `retry_jitter`, `max_queue_size`, `response_mode`, `created_at`, `updated_at`, `version`

### `settings` table
Key-value store for app-level settings: `currentProviderClaude`, `currentProviderCodex`, `common_config_claude`, `common_config_codex`, etc.

## Common Issues & Fixes

### 1. CC Switch can't detect Codex

**Symptom:** CC Switch shows "Codex not found" or codex toggle is greyed out.

**Root cause:** The `codex` binary symlink in PATH is broken. CC Switch scans `PATH` for the `codex` executable.

**Fix:**
```bash
# The actual binary is inside the Codex.app bundle
/Applications/Codex.app/Contents/Resources/codex --version

# Create proper symlinks
sudo ln -sf /Applications/Codex.app/Contents/Resources/codex /usr/local/bin/codex
sudo ln -sf /Applications/Codex.app/Contents/Resources/codex /usr/local/bin/codex-cli
```

Also ensure `~/.codex/auth.json` has a valid API key (see issue #3).

### 2. Claude Code model error through CC Switch proxy

**Symptom:** `claude -p "..."` returns `"There's an issue with the selected model (claude-opus-4-8[1m])..."`

**Root cause:** CC Switch's `~/.claude/settings.json` sets `ANTHROPIC_DEFAULT_*_MODEL` to Claude official model names (e.g. `claude-opus-4-8[1M]`), but the proxy only serves DeepSeek models. Claude Code validates model names against the proxy's `/v1/models` response.

**Fix:** The settings.json is managed by CC Switch — you can't edit it directly (CC Switch overwrites it on restart). Instead, fix the underlying proxy configuration so the proxy properly forwards requests. See issue #4 and #5.

### 3. API key expired in CC Switch database

**Symptom:** Proxy returns `upstream_error` with HTTP 401 or 404. Logs show `[FWD-003] Provider DeepSeek 请求失败: 上游 HTTP 401`.

**Root cause:** CC Switch stores API keys in the `providers.settings_config` JSON field. When the key expires, the old key persists in the DB even if `.env` has a new key.

**Fix:** Update the key in the CC Switch database:
```bash
# Get the current valid key
KEY=$(python3 -c "
with open(os.path.expanduser('~/.hermes/.env')) as f:
    for line in f:
        if line.startswith('DEEPSEEK_API_KEY='):
            print(line.split('=', 1)[1].strip())
            break
")

# Update Claude provider
sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE providers SET settings_config = json_set(settings_config, '\$.env.ANTHROPIC_AUTH_TOKEN', '$KEY') WHERE id='4ed7a616-43a5-4cc6-ac77-c0d2acc64f61';"

# Update Codex provider
sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE providers SET settings_config = json_set(settings_config, '\$.auth.OPENAI_API_KEY', '$KEY') WHERE id='cd2cb0b5-5609-4380-bc7f-361c6befcf89';"

# Update Codex auth.json
echo "{\"OPENAI_API_KEY\": \"$KEY\"}" > ~/.codex/auth.json
```

Then restart CC Switch for changes to take effect.

### 4. Wrong apiFormat for DeepSeek Claude proxy

**Symptom:** Proxy logs show `>>> 请求 URL: https://api.deepseek.com/v1/responses (model=deepseek-v4-pro)` followed by `上游 HTTP 404`.

**Root cause:** The Claude provider's `meta.apiFormat` is set to `openai_responses`, but DeepSeek does NOT support OpenAI Responses API (`/v1/responses` returns 404). DeepSeek supports:
- ✅ Anthropic format: `/anthropic/v1/messages` (200)
- ✅ OpenAI Chat format: `/v1/chat/completions` (200)
- ❌ OpenAI Responses API: `/v1/responses` (404)

**Fix:**
```bash
sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE providers SET meta = json_set(meta, '\$.apiFormat', 'anthropic') WHERE id='4ed7a616-43a5-4cc6-ac77-c0d2acc64f61';"
```

Then restart CC Switch.

### 5. Wrong endpoint URL for DeepSeek

**Symptom:** Proxy logs show `>>> 请求 URL: https://api.deepseek.com/v1/messages` (missing `/anthropic` prefix) followed by `上游 HTTP 404`.

**Root cause:** The `provider_endpoints.url` is `https://api.deepseek.com` but the proxy appends `/v1/messages`, producing `https://api.deepseek.com/v1/messages` (404). It should be `https://api.deepseek.com/anthropic` so the full URL becomes `https://api.deepseek.com/anthropic/v1/messages` (200).

**Fix:**
```bash
sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE provider_endpoints SET url='https://api.deepseek.com/anthropic' WHERE provider_id='4ed7a616-43a5-4cc6-ac77-c0d2acc64f61';"

sqlite3 ~/.cc-switch/cc-switch.db \
  "UPDATE providers SET settings_config = json_set(settings_config, '\$.env.ANTHROPIC_BASE_URL', 'https://api.deepseek.com/anthropic') WHERE id='4ed7a616-43a5-4cc6-ac77-c0d2acc64f61';"
```

Then restart CC Switch.

### 6. Restarting CC Switch

```bash
# Kill
pkill -f "cc-switch" 2>/dev/null
sleep 2
# Start (launches in background, silent startup)
open /Applications/CC\ Switch.app
# Verify
sleep 3
ps aux | grep "cc-switch" | grep -v grep
# Check logs
tail -20 ~/.cc-switch/logs/cc-switch.log
```

CC Switch starts in "silent startup" mode (tray only, no window). Verify the proxy is listening:
```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:15721/v1/models
# Should return 200
```

## DeepSeek API Compatibility Matrix

| Endpoint | Method | Works? | Used By |
|----------|--------|--------|---------|
| `https://api.deepseek.com/anthropic/v1/messages` | POST | ✅ 200 | Claude Code (via CC Switch proxy with `apiFormat: anthropic`) |
| `https://api.deepseek.com/v1/chat/completions` | POST | ✅ 200 | Codex (via CC Switch proxy with `apiFormat: openai_chat`) |
| `https://api.deepseek.com/v1/responses` | POST | ❌ 404 | NOT supported — OpenAI Responses API not implemented |
| `https://api.deepseek.com/v1/models` | GET | ✅ 200 | Model listing |
| `https://api.deepseek.com/anthropic/v1/models` | GET | ✅ 200 | Model listing (Anthropic format) |

## Proxy Request Flow (Fixed Configuration)

```
Claude Code
  → settings.json: ANTHROPIC_BASE_URL=http://127.0.0.1:15721
  → POST http://127.0.0.1:15721/v1/messages
  → CC Switch Proxy translates to Anthropic format
  → POST https://api.deepseek.com/anthropic/v1/messages
  → DeepSeek responds with Anthropic-format response
  → Proxy returns response to Claude Code

Codex
  → config.toml: base_url=http://127.0.0.1:15721/v1
  → POST http://127.0.0.1:15721/v1/chat/completions
  → CC Switch Proxy translates to OpenAI Chat format
  → POST https://api.deepseek.com/v1/chat/completions
  → DeepSeek responds with Chat Completions response
  → Proxy returns response to Codex
```

## Verification Commands

After fixing, verify the full chain works:

```bash
# 1. Proxy is running
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:15721/v1/models

# 2. Claude Code works
claude -p "hello, respond with just 'ok'" --max-turns 1

# 3. Codex works
codex --version

# 4. CC Switch is running
ps aux | grep "cc-switch" | grep -v grep
```
