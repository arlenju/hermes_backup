---
name: auto-inventory-docs
description: >-
  Auto-generate and maintain inventory documentation (skills, plugins, config)
  as markdown files, synced to GitHub via cron + no_agent Python scripts.
  Covers the full pipeline: filesystem scan → markdown generation → git commit → push.
version: 1.0.0
tags: [automation, documentation, cron, github, inventory]
---

# Auto-Inventory Documentation

Generate and maintain living inventory docs of your Hermes Agent setup —
skills, plugins, config, or any state readable from the filesystem.

## When to Use

- User asks "keep this list updated" or "sync this to GitHub"
- User installs skills/plugins and wants the inventory to auto-track
- A setup artifact needs version-controlled history with zero manual effort
- Any recurring documentation that should reflect current filesystem state

## Workflow

### 1. Write the Collector Script

Create a no-dependencies Python script under `~/.hermes/scripts/`:

```python
#!/usr/bin/env python3
"""One-shot inventory generator — scans fs, writes markdown, git push."""
import os, re, subprocess
from pathlib import Path
from datetime import datetime

HERMES_HOME = Path.home() / ".hermes"
# ... scanning logic reading SKILL.md frontmatter ...
INVENTORY = Path.home() / "My_Project" / "hermes_agent" / "Hermes-Agent" / "SKILLS_INVENTORY.md"

def git_push(): ...
def generate_markdown(data): ...

if __name__ == "__main__":
    data = scan_skills()
    content = generate_markdown(data)
    INVENTORY.write_text(content)
    git_push()
```

Key design rules:
- **Self-contained** — no pip deps, no venv activation needed
- **Idempotent** — `git diff --quiet` check before commit; no-op if unchanged
- **Resilient** — `try/except` around git operations; reports but doesn't crash
- **Fast** — pure filesystem reads, runs in <1s

### 2. Create the Cron Job

```bash
hermes cron create \
  --name "Update Skills Inventory" \
  --schedule "0 3 * * *" \       # daily at 3am
  --script update_skills_inventory.py \  # relative to ~/.hermes/scripts/
  --no-agent \                    # no LLM cost, script output delivered verbatim
  --workdir /path/to/repo         # git operations run here
```

**Script path rules:**
- Must live under `~/.hermes/scripts/`
- Pass ONLY the filename (relative) — no absolute or `~/` paths
- `.sh`/`.bash` → bash; everything else → Python

**no_agent=True semantics:**
- Script stdout → delivered as the cron result
- Empty stdout → silent (nothing sent to user)
- Script exit code ≠ 0 → error alert
- `prompt` and `skills` fields are IGNORED

### 3. Test the Pipeline

```bash
# Run the script directly
python3 ~/.hermes/scripts/update_skills_inventory.py

# Force-run the cron job to verify
hermes cron run <job-id>

# Check history
hermes cron list
```

### 4. Verify the Artifact

```bash
# Check the generated file
cat path/to/INVENTORY.md

# Confirm it's on GitHub
gh repo view arlenju/hermes_backup  # or your repo
```

## Common Pitfalls

1. **Absolute script path rejected.** Cron job `script=` field takes only a filename relative to `~/.hermes/scripts/`. If the file is already there, just pass the basename.

2. **no_agent vs regular cron.** Use `no_agent=True` for deterministic data → output jobs (inventory updates, disk checks, threshold alerts). Use regular agent cron for jobs that need reasoning (summarize latest feed, pick interesting items).

3. **Git push rejects from diverged remote.** Remote may have diverged. The script handles this with `try/except` — it reports the error but doesn't destroy local data. A manual `git pull --rebase` every few months may be needed.

4. **Multiple cron jobs → same repo → rebase conflicts.** If two cron jobs (e.g., config backup at 00:00 and skills inventory at 03:00) both push to the same repo, they can conflict. When the second job runs `git pull --rebase` and encounters unstaged changes from the previous job's commit, the rebase fails with `cannot pull with rebase: You have unstaged changes`. Then `git push` fails with `non-fast-forward`.

   **Fix manually when this happens:**
   ```bash
   cd ~/.hermes_backup_repo
   git rebase --abort        # abort stuck rebase
   git reset --hard origin/main  # reset to remote state
   ```
   Then re-run the script to regenerate and push.

   **Prevention:** Stagger the schedules so they don't collide. Or have one script own the entire update cycle.

5. **Stale content.** If the script only parses `~/.hermes/skills/` and a skill was installed elsewhere (e.g. a hub skill from a plugin), the scan may undercount. Check the actual skills list: `hermes skills list | wc -l` vs script output.

## References

- `references/skills-inventory-setup.md` — Full session log: script creation, testing, cron setup for skills inventory
