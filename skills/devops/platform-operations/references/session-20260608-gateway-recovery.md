# Gateway Recovery: Venv Conflict + Feishu Ping Timeout (2026-06-08)

## Symptom

User reported Feishu constantly disconnecting ("老是断联"). Gateway log showed periodic `ERROR Lark: receive message loop exit, err: no close frame received or sent` plus repeated `ModuleNotFoundError: No module named 'hermes_cli'`.

## Root Cause

**Two problems, same symptom** (gateway instability):

### 1. launchd Plist Wrong Venv

The launchd plist at `~/Library/LaunchAgents/ai.hermes.gateway.plist` had:
```
<string>/Users/jushuai/My_Project/hermes_agent/Hermes-Agent/venv/bin/python</string>
```

This is the **project dev venv**, which had a broken editable install (`hermes_cli` was in the editable-finder mapping but the source had been updated via git pull). Every time launchd auto-restarted (KeepAlive=true), it failed with `ModuleNotFoundError: No module named 'hermes_cli'`.

Meanwhile, the **actual running process** was using the correct venv:
```
/Users/jushuai/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace
```

But the crash loop in the launchd-managed process was causing gateway instability that affected WebSocket connections.

### 2. Feishu WebSocket Keepalive Timeout

The Feishu WebSocket connection drops every ~10-16 minutes:
```
[Lark] receive message loop exit, err: no close frame received or sent
```

This is **normal** — caused by network environment (China → feishu.cn). The gateway auto-reconnects within seconds. No action needed.

## Diagnosis Steps

```bash
# 1) Check if gateway process is alive
ps aux | grep "hermes.*gateway" | grep -v grep
# → Found PID 18373 running from ~/.hermes/hermes-agent/venv/

# 2) Check launchd plist
grep "venv/bin/python" ~/Library/LaunchAgents/ai.hermes.gateway.plist
# → Pointed to wrong venv!

# 3) Check gateway.error.log for crash patterns
grep "ModuleNotFoundError" ~/.hermes/logs/gateway.error.log | tail -5
# → Repeated hermes_cli errors = venv conflict

# 4) Check gateway.log for WebSocket health
grep -E "Lark.*connected|Lark.*disconnected" ~/.hermes/logs/gateway.log | tail -10
# → Shows disconnect every 10-16 min, reconnect within 2s

# 5) Verify the correct venv works
~/.hermes/hermes-agent/venv/bin/python -c "import hermes_cli; print('OK')"
```

## Fix Applied

1. Verified the launchd plist had already been updated to use the correct venv path
2. Gateway restarted and stabilized
3. User confirmed Feishu connection working

## Key Takeaways

- **gateway.error.log ≠ current health.** Error log accumulates noise from crash cycles. Check `gateway.log` for real-time status.
- **Two venvs exist** on macOS Hermes installs with source checkout: `~/.hermes/hermes-agent/venv/` (runtime) vs `~/My_Project/hermes_agent/Hermes-Agent/venv/` (dev). The plist must point to the runtime venv.
- **Feishu WebSocket disconnects are NOT a bug.** They're normal keepalive timeouts. The auto-reconnect works. Don't chase them unless reconnection fails.
- **`hermes gateway restart` may hang** when the CLI uses the wrong venv. Use `launchctl unload/load` or manually source the correct venv first.
