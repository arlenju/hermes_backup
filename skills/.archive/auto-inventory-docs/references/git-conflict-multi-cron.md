# Skills Inventory + Backup Git Conflict (2026-06-07)

## Symptom

Backup script (`hermes_backup.sh`) failed with:
```
error: cannot pull with rebase: You have unstaged changes.
...
CONFLICT (content): Merge conflict in memories/MEMORY.md
CONFLICT (content): Merge conflict in memories/USER.md
error: could not apply 856618e... 自动备份...
```

## Root Cause

Two cron jobs push to the same repo (`arlenju/hermes_backup`):

| Job | Schedule | Script | Type |
|-----|----------|--------|------|
| Config backup | 00:00 daily | `hermes_backup.sh` | agent cron |
| Skills inventory | 03:00 daily | `update_skills_inventory.py` | no_agent |

The inventory script pushes `SKILLS_INVENTORY.md` at 03:00. When the backup script later tries `git pull --rebase origin main`, the local repo has uncommitted changes from the inventory script's commit (because `git pull --rebase` was the first step, followed by `cp`, then `git add -A`). The rebase fails because the working tree isn't clean.

## Fix

```bash
cd ~/.hermes_backup_repo
git rebase --abort        # abort stuck rebase
git checkout -- .         # discard uncommitted changes
git clean -fd             # remove untracked files
git reset --hard origin/main  # match remote exactly
```

Then re-run the failing script.

## Prevention

- Stagger schedules with enough gap (00:00 + 03:00 is fine, but the backup script's `git pull` step happens at 00:00 while inventory pushes at 03:00 — the conflict window is the NEXT day's backup run)
- Better fix: Have the backup script start with `git stash push` and end with `git stash pop`
