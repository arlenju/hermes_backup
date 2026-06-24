---
name: cron-job-toolset-pitfalls
description: Common cron job failures caused by insufficient or wrong enabled_toolsets, and how to diagnose/fix them.
type: reference
---

# Cron Job Toolset Pitfalls

Cron jobs run in a fresh session with no user present. The `enabled_toolsets` field controls which tools the agent can call. If the set is too narrow, the agent may hallucinate tool names (e.g. `bash`) or fail silently.

## Symptom: "Model generated invalid tool call: bash"

The cron job output shows:

```
RuntimeError: Model generated invalid tool call: bash
```

**Root cause:** The cron job's `enabled_toolsets` only includes `["cronjob"]` (or another narrow set), but the prompt asks the agent to run scripts, read files, or inspect system state. The model tries to call `bash` (which doesn't exist as a Hermes tool — the correct tool is `terminal`) and crashes.

**Fix:** Add `terminal` and `file` to the cron job's `enabled_toolsets`:

```bash
hermes cron update <job-id> --toolsets cronjob,terminal,file
```

Or via the API:

```python
cronjob(action="update", job_id="...", enabled_toolsets=["cronjob", "terminal", "file"])
```

## Symptom: Cron runs silently, no output, no delivery

The cron job's `last_status` shows `ok` but nothing was delivered to the user.

**Root cause (most common):** The agent's final response was `[SILENT]` because the cron prompt says "If there is genuinely nothing new to report, respond with exactly `[SILENT]`". If the agent can't actually check anything (missing tools), it defaults to silent.

**Fix:** Same as above — add the tools the agent needs to actually perform the checks.

## Symptom: Cron job hangs until timeout

The cron job runs for the full timeout duration and then fails.

**Root cause:** The agent is trying to use a tool that's not available in its toolset. The tool call fails, the agent retries or tries an alternative, that also fails, and the loop continues until timeout.

**Fix:** Check `enabled_toolsets` first. If the prompt mentions checking files, running scripts, or calling APIs, ensure the corresponding toolsets are included.

## General Rule for enabled_toolsets

| What the prompt needs | Minimum toolsets |
|---|---|
| List/check cron jobs only | `["cronjob"]` |
| Run a shell script | `["terminal"]` |
| Read/write files | `["file"]` |
| List cron + run script + read output | `["cronjob", "terminal", "file"]` |
| Search past sessions | `["session_search"]` |
| Web research | `["web"]` |
| Full agent capabilities | omit `enabled_toolsets` entirely (uses all defaults) |

## How to Diagnose a Failed Cron Job

```bash
# 1. List all cron jobs and check last_status
cronjob action=list

# 2. Read the last run output
ls -lt ~/.hermes/cron/output/<job-id>/
cat ~/.hermes/cron/output/<job-id>/<latest-file>.md

# 3. Check the Error section in the output file for the exact error message
```

## How to Fix (via CLI)

```bash
# Update toolsets for an existing job
hermes cron update <job-id> --toolsets cronjob,terminal,file

# Or run the job immediately to test the fix
hermes cron run <job-id>
```

## How to Fix (via skill API)

```python
cronjob(action="update", job_id="...", enabled_toolsets=["cronjob", "terminal", "file"])
cronjob(action="run", job_id="...")  # verify
```

## Prevention

When creating a new cron job, always ask: "What tools will the agent need to fulfill this prompt?" If the prompt says "run script", add `terminal`. If it says "read file", add `file`. If it says "check cron jobs", add `cronjob`. When in doubt, omit `enabled_toolsets` to give the agent full access.

## Reference

- Hermes cron job docs: https://hermes-agent.nousresearch.com/docs/features/cron
- `model-fallback` SKILL.md — cron job examples for model health monitoring
