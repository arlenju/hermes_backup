# macOS Gateway: launchd vs Background Process

## The launchctl exit 5 Problem

On some macOS versions, `hermes gateway restart` may fail with:

```
Bootstrap failed: 5: Input/output error
⚠ launchd cannot manage the gateway on this macOS version (launchctl exit 5).
✓ Started gateway as a background process instead
  It will NOT auto-start at login or auto-restart on crash.
```

**Root cause:** Apple changed the launchd bootstrap API in recent macOS versions. On **macOS 26.3 (Tahoe)**, ALL launchctl commands (`bootout`, `bootstrap`, `load`, `unload`, `enable`, `start`, `kickstart`) fail with exit code 5 / "Input/output error" when targeting user-domain services. The `hermes gateway install` + `hermes gateway start` two-step appears to succeed (returning "✓ Service started") but launchd does NOT actually load the service — `launchctl list` shows `- 1 ai.hermes.gateway` (dead, not loaded).

**Launchd is non-functional on macOS 26.3+ for user-level services.** Skip it entirely.

### Real Fix: caffeinate + Background Gateway

On macOS 26.3+, use `caffeinate` to prevent sleep while the gateway runs as a background process:

```bash
# 1. Start caffeinate (prevents idle, display, and system sleep — 24h assertion)
nohup caffeinate -d -i -m -t 86400 > /dev/null 2>&1 &

# 2. Verify caffeinate is running
pgrep caffeinate

# 3. Start gateway
nohup /Users/jushuai/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run --replace \
  >> ~/.hermes/logs/gateway.log 2>&1 &
```

**Combined wrapper script** (place at `/Users/jushuai/.hermes/gateway-wrapper.sh`):
```bash
#!/bin/bash
set -e
CAFFEINATE_PID=""
cleanup() { [ -n "$CAFFEINATE_PID" ] && kill "$CAFFEINATE_PID" 2>/dev/null; }
trap cleanup EXIT
/usr/bin/caffeinate -d -i -m -t 86400 &
CAFFEINATE_PID=$!
exec /Users/jushuai/.hermes/hermes-agent/venv/bin/python \
  -m hermes_cli.main gateway run --replace
```

Run: `nohup /Users/jushuai/.hermes/gateway-wrapper.sh >> ~/.hermes/logs/gateway.log 2>&1 &`

### Limitations of caffeinate approach

- Does NOT auto-start on login (no launchd to run it)
- Does NOT auto-restart on crash (unless wrapped in a restart loop)
- **Does prevent lid-close sleep** — the primary concern

### Alternative: crontab @reboot

For auto-start on login without launchd:
```
@reboot ~/.hermes/hermes-agent/venv/bin/hermes gateway start
```
Add with `crontab -e` (start will fall back to nohup on macOS 26.3).

## Verification

```bash
hermes gateway status
```

Expected healthy state:
```
✓ Service definition matches the current Hermes install
✓ Gateway service is loaded
{
    "OnDemand" = false;
    "PID" = 80233;
    ...
}
```

Check logs for platform connections:
```bash
grep -E "(weixin connected|feishu.*connected|connected to)" ~/.hermes/logs/gateway.log | tail -5
```

Expected:
```
✓ weixin connected
[Lark] [INFO] connected to wss://msg-frontier.feishu.cn/ws/v2?...
```

## What launchd Mode Provides

| Feature | launchd mode | Background fallback |
|---------|-------------|---------------------|
| Receiving messages | ✅ | ✅ |
| Sending messages | ✅ | ✅ |
| Cron jobs | ✅ | ✅ |
| Auto-start on login | ✅ | ❌ |
| Auto-restart on crash | ✅ | ❌ |
| **Auto-restart after sleep/lid-close** | ✅ | ❌ |
| `hermes gateway stop` | ✅ | ✅ |

The key benefit of launchd mode on macOS: **KeepAlive=true** means the gateway survives lid-close/sleep cycles. When the Mac wakes up, launchd re-launches the gateway and WebSocket connections re-establish automatically. Background (nohup) mode dies on sleep and stays dead.

## What launchd Handles

- **Lid close / sleep → wake**: launchd keeps the plist loaded. On wake, the gateway process resumes where it left off, or if it was killed during sleep, launchd restarts it fresh (KeepAlive=true).
- **Crash recovery**: if the gateway process exits unexpectedly, launchd re-launches it within seconds.
- **Login auto-start**: gateway starts as soon as you log in (RunAtLoad=true).

## Legacy: Background Fallback Procedure

If launchd truly cannot be made to work (e.g., macOS 25.x or older Hermes version), use the background process fallback:

```bash
# 1. Stop the old gateway first
hermes gateway stop
sleep 3

# 2. Start as background process
hermes gateway start
```

Or the single command (which will fall back to nohup if launchd fails):

```bash
hermes gateway restart
```

### Workarounds for Auto-Restart Without launchd

1. Use a simple cron job (`@reboot`):
   ```
   @reboot ~/.hermes/hermes-agent/venv/bin/hermes gateway start
   ```
   Add with `crontab -e`.

2. Use a terminal-based supervisor like `tmux` + `respawn`:
   ```bash
   tmux new-session -d -s gateway 'while true; do ~/.hermes/hermes-agent/venv/bin/hermes gateway start; sleep 5; done'
   ```

## Plist Details

Location: `~/Library/LaunchAgents/ai.hermes.gateway.plist`

Key settings:
- `KeepAlive: true` — auto-restart on crash and after sleep
- `RunAtLoad: true` — auto-start on login
- `LimitLoadToSessionType: [Aqua, Background]` — runs in both GUI and background sessions

To inspect:
```bash
cat ~/Library/LaunchAgents/ai.hermes.gateway.plist
```

## Pitfalls

- **Stale plist after Hermes update**: Run `hermes gateway install` after updating Hermes to refresh the service definition. The plist contains the venv Python path which changes between versions.
- **Service loaded but process gone**: If `hermes gateway status` shows "Service is loaded" but no PID, launchd is waiting to restart it (may happen if the process crashed and KeepAlive is throttling restarts). Wait 10s or run `launchctl kickstart -k gui/$(id -u)/ai.hermes.gateway` to force an immediate restart.
- **`hermes gateway restart` hits exit 5 but `install + start` works**: This is expected on macOS 26.x — `restart` tries to bootstrap directly, while `install` uses the more compatible plist-registration path.
- **Wrong Hermes install path in plist**: If you installed Hermes to a non-default location, the plist may point at the old path. Run `hermes gateway install` to fix.
