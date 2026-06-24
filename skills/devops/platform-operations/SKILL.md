---
name: platform-operations
description: Diagnose, troubleshoot, and operate Hermes messaging platforms (WeChat, Feishu, etc.). Covers connection checks, log analysis, gateway restart, and message delivery patterns.
---

# Platform Operations

Diagnose and fix Hermes messaging platform connection issues, check platform health, and send messages to connected platforms.

## When to Load

- User asks "check if X is working" or "X is disconnected"
- User reports a platform showing "connection failed" / "暂时无法连接"
- User asks to send a message to a specific platform
- Gateway-related issues or platform outage reports

## Architecture Quick Reference

Hermes gateway runs as a background process connecting to multiple messaging platforms:

```
gateway process → weixin (ilinkai bridge)
                → feishu (WebSocket)
                → telegram, discord, etc.
```

State is tracked in:
- `~/.hermes/gateway_state.json` — live connection status
- `~/.hermes/logs/gateway.log` — detailed connection and message events
- `~/.hermes/logs/errors.log` — warnings and errors (WARNING+)
- `~/.hermes/channel_directory.json` — known contacts/channels per platform

## Diagnostic Workflow

### 1. Check Gateway State

```bash
cat ~/.hermes/gateway_state.json
```

Key fields:
- `gateway_state`: `"running"` (healthy), `"draining"` (shutting down)
- `platforms[].state`: `"connected"` or error details
- `pid`: process ID — verify process is alive with `ps`

### 2. Check Logs for Platform Issues

```bash
# WeChat/weixin: look for send failures, rate limits, disconnects
grep -i "weixin\|wechat" ~/.hermes/logs/gateway.log | grep -i "error\|fail\|warn\|rate\|disconnect"

# Feishu: look for WebSocket errors
grep -i "feishu\|lark" ~/.hermes/logs/gateway.log | grep -i "error\|fail\|warn\|disconnect"

# General errors
grep -i "weixin\|wechat\|feishu\|lark" ~/.hermes/logs/errors.log | tail -20
```

Common weixin error patterns:
- `send chunk failed to=... attempt=1/5, retrying` — transient, may self-recover
- `iLink sendmessage rate limited` — throttled by ilinkai, backoff built in
- `Server disconnected` / `poll error (1/3): Server disconnected` — bridge connection lost, **usually auto-recovers** within seconds. Check subsequent log lines: if inbound messages appear right after, the reconnection succeeded automatically. Only needs gateway restart if `poll error (3/3)` (all retries exhausted) or disconnection persists > 30s with no reconnection log.

Common feishu error patterns:
- `no close frame received or sent` — WebSocket disconnected uncleanly
- `connect failed: HTTPSConnectionPool...ProxyError` — proxy/network issue
- `receive message loop exit` — WebSocket reconnection cycle

### 3. Check Channel Directory

```bash
cat ~/.hermes/channel_directory.json
```

Platforms with empty arrays have no registered contacts yet — messages first received from that platform populate the directory.

### 4. Verify Gateway Process is Running

```bash
ps aux | grep "hermes.*gateway" | grep -v grep
```

If no process found, the gateway has crashed or was killed (check for SIGTERM in last log lines).

## macOS Screen Sharing / VNC Recovery

When the user can't remote into their Mac (noVNC or Screen Sharing), the issue is often that `screensharingd` is registered but **not running**.

### Diagnostic

```bash
# Check if screensharingd is registered
launchctl print system/com.apple.screensharing 2>&1 | grep "state"
# → "state = not running" means it's registered but stopped

# Check if VNC port is listening
lsof -i :5900 2>/dev/null
# → empty = not listening

# Check if noVNC websockify is running
lsof -i :6080 2>/dev/null
```

### Fix (no sudo needed)

```bash
# Start screensharingd directly (works without sudo on macOS)
launchctl kickstart -k system/com.apple.screensharing

# Verify
sleep 2
nc -z 127.0.0.1 5900 && echo "5900 OPEN" || echo "5900 CLOSED"
```

This starts the Screen Sharing daemon and opens port 5900. The noVNC bridge (websockify on port 6080 forwarding to 127.0.0.1:5900) then works immediately.

### When sudo IS available (alternative)

```bash
sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.screensharing.plist
```

### Pitfalls

- **No sudo in terminal** — `launchctl kickstart -k system/com.apple.screensharing` works without sudo
- **Screen Sharing enabled in System Settings but daemon not running** — this happens after system updates or sleep/wake cycles. The kickstart command restarts it without toggling the preference
- **noVNC running but 5900 closed** — the websockify process on 6080 is fine, but the backend VNC server (screensharingd) isn't serving. Fix the backend, not the websockify
- **`computer_use` tool not available** — the `macos-computer-use` skill requires the `computer_use` tool to be enabled via `hermes tools`. If it's not available, use terminal-based approaches (launchctl, AppleScript, osascript) instead

### Launchd Mode (Recommended — survives lid-close/sleep)

On macOS versions **prior to 26.3 (Tahoe)**:

```bash
# 1. Repair/update the launchd plist
hermes gateway install

# 2. Start via launchd
hermes gateway start
```

This provides auto-start on login, auto-restart on crash, and auto-recovery after lid-close/sleep.

### macOS 26.3+ — launchd Broken, Use caffeinate

On **macOS 26.3 (Tahoe)** and later, launchctl bootstrap/bootout commands all fail with exit 5 / "Input/output error". Launchd **cannot** manage user-level services. Use `caffeinate` to prevent lid-close sleep instead:

```bash
# Start caffeinate (24h assertion against idle/display/system sleep)
nohup caffeinate -d -i -m -t 86400 > /dev/null 2>&1 &

# Start gateway
nohup /Users/jushuai/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run --replace \
  >> ~/.hermes/logs/gateway.log 2>&1 &
```

Or use the combined wrapper script at `/Users/jushuai/.hermes/gateway-wrapper.sh`.

See `references/macos-launchd-gateway-notes.md` for full details and limitations.

### Background Fallback

If `hermes gateway start` falls back to background process (nohup), the gateway will NOT auto-restart after sleep or crash:

```
⚠ launchd cannot manage the gateway on this macOS version (launchctl exit 5).
✓ Started gateway as a background process instead
```

**Verification:** Check the new PID — `hermes gateway status` will show a warning about the service not being loaded but will list the running PID. Check logs for successful WebSocket connections. Also run `hermes status --all` for a complete health overview.

See also: `references/macos-launchd-gateway-notes.md`

## Sending Messages to Platforms

Use `send_message()` tool:

```python
# First, discover available targets:
send_message(action="list")
# Returns: Available targets with platform:chat_id format

# Bare platform → home channel (must be configured)
send_message(target="feishu", message="...")

# Platform:chat_id → specific chat
send_message(target="feishu:oc_xxxxx", message="...")

# Platform:user_id → specific user
send_message(target="weixin:o9cq809...", message="...")
```

**Always call `send_message(action='list')` first** when the user says "send to platform X" without specifying a chat — it's the only reliable way to get the correct chat_id format for each platform.

### Voice Message Delivery (TTS → Native Voice Bubble)

Both WeChat and Feishu support native voice bubbles when audio is delivered in platform-specific formats via the `MEDIA:` tag:

| Platform | Format | Conversion | MEDIA: tag |
|----------|--------|------------|------------|
| WeChat | SILK v3 | `TTS→MP3→WAV→PCM→pysilk.encode()→.silk` | `MEDIA:file.silk` |
| Feishu | OGG Opus | `ffmpeg -c:a libopus -b:a 24k -ar 24000 -ac 1` | `MEDIA:file.opus` |

**Workflow:**
1. Generate TTS audio with `text_to_speech()` or `edge-tts` → MP3
2. Convert to platform format (SILK for WeChat, OGG Opus for Feishu)
3. Send with `send_message(target="...", message="MEDIA:/path/to/file")`

See `voice-pipeline` skill for detailed conversion scripts (`scripts/mp3_to_silk.py`, `scripts/mp3_to_feishu_opus.py`).

### Feishu Target Formats

Feishu uses three ID tiers — see `references/feishu-id-types.md` for details:

| Format | Type | Example |
|--------|------|---------|
| `oc_xxx` | chat_id (DM or group) | Used as `feishu:oc_xxx` |
| `ou_xxx` | open_id (user) | Handled automatically when passed as chat_id |
| `cli_xxx` | app_id (NOT a user ID) | Cannot receive messages directly |

### Weixin/WeChat Target Format

```python
send_message(target="weixin:o9cq809...@im.wechat", message="...")
```

## Pitfalls

- **Wrong venv**: The project dev venv (`Hermes-Agent/venv/`) lacks `hermes_cli`. Always use `~/.hermes/hermes-agent/venv/`.
- **channel_directory is empty for new platforms**: This is normal — contacts only appear after the platform receives a message.
- **app_id vs open_id confusion**: Users often provide `cli_xxx` (app credential) thinking it's their user ID. The correct user identifier is `ou_xxx` (open_id).
- **Gateway killed by systemd/SIGTERM**: Systems with OOM or auto-scaling may kill the gateway. Restart with `hermes gateway run --replace`.
- **send_message returns "No home channel set"**: Set `FEISHU_HOME_CHANNEL` or `WEIXIN_HOME_CHANNEL` in `.env`, or pass chat_id explicitly.
- **Don't guess target IDs**: Always call `send_message(action='list')` first to get the correct `platform:chat_id` format. ID formats vary (`oc_xxx` for Feishu, `o9cq809...@im.wechat` for WeChat, `-1001234567890:thread_id` for Telegram topics).

## Multiple-Venv Conflict

Hermes can have two venvs that look similar but one is broken:

| Venv | Purpose | Status |
|------|---------|--------|
| `~/.hermes/hermes-agent/venv/` | **Runtime venv** (Hermes install) | ✅ Has `hermes_cli` |
| `~/My_Project/hermes_agent/Hermes-Agent/venv/` | **Dev venv** (source checkout) | ⚠️ May lack `hermes_cli` |

**Symptom:** `ModuleNotFoundError: No module named 'hermes_cli'` in `gateway.error.log`.

**Diagnosis:**
```bash
# Which venv is launchd configured to use?
grep "venv/bin/python" ~/Library/LaunchAgents/ai.hermes.gateway.plist

# Which venv is the ACTUAL running process using?
ps aux | grep "hermes.*gateway" | grep -v grep

# Test a venv directly:
~/.hermes/hermes-agent/venv/bin/python -c "import hermes_cli; print('OK')"
```

**Fix:** Update the launchd plist to point to `~/.hermes/hermes-agent/venv/bin/python`, then restart:
```bash
launchctl unload ~/Library/LaunchAgents/ai.hermes.gateway.plist
launchctl load ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Feishu WebSocket Disconnect Is Normal

Feishu WebSocket connections **routinely disconnect** every 10–16 minutes:
```
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?... [conn_id=XXX]
[Lark] [ERROR] no close frame received or sent [conn_id=XXX]
[Lark] [INFO] disconnected ... [conn_id=XXX]
[Lark] [INFO] trying to reconnect for the 1st time
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?... [conn_id=YYY]
```

This is **not a problem** — the gateway auto-reconnects immediately. The cycle is caused by network environment keepalive timeouts, not a bug. Verify by checking that the `[INFO] connected` log appears within 30s of each disconnect. If reconnection hangs or shows `ProxyError`, there's a network issue.

## Gateway Error Log Trap

`~/.hermes/logs/gateway.error.log` accumulates noise from crash-recovery cycles:
- `ModuleNotFoundError: No module named 'hermes_cli'` — indicates wrong-venv issue (see above)
- These are **not current runtime errors** — they're from failed restart attempts that happened BEFORE the current running process

To check current gateway health, use `~/.hermes/logs/gateway.log` instead (INFO level, real-time). A healthy gateway shows:
- `Gateway running with N platform(s)`
- `Channel directory built: N target(s)`
- Platform-specific connection messages
