# Skills Inventory — Setup Reference

**Date:** 2026-06-06
**User:** arlenju (GitHub) / 帅哥

## The Script

`~/.hermes/scripts/update_skills_inventory.py` (8.4KB, Python 3)

### What it does:
1. Scans `~/.hermes/skills/` recursively — detects category dirs (e.g. `skills/creative/`) vs flat skill dirs (e.g. `skills/prism-scan/`)
2. Parses YAML frontmatter from each `SKILL.md` for name, description, category
3. Generates a markdown inventory with 18+ categorized sections, icons, numbered entries, and a summary table
4. Writes to `~/My_Project/hermes_agent/Hermes-Agent/SKILLS_INVENTORY.md`
5. Runs `git add + commit + push` only if file changed

### Key design decisions:
- **No dependencies** — pure stdlib (pathlib, re, subprocess, datetime)
- **No venv** — runs with system Python 3
- **Dual-depth scanner** — handles both `skills/<cat>/<name>/SKILL.md` and `skills/<name>/SKILL.md`
- **Idempotent push** — `git diff --quiet` check before commit

## The Cron Job

```
Name:     Update Skills Inventory
Schedule: 0 3 * * *  (daily at 3am UTC+8)
Type:     no_agent (script-only, no LLM)
Script:   update_skills_inventory.py  (relative to ~/.hermes/scripts/)
Workdir:  /Users/jushuai/My_Project/hermes_agent/Hermes-Agent
Deliver:  origin (back to the chat that created it)
```

## Verification Commands

```bash
# Test the script
python3 ~/.hermes/scripts/update_skills_inventory.py

# Check cron jobs
hermes cron list

# View the generated file
cat ~/My_Project/hermes_agent/Hermes-Agent/SKILLS_INVENTORY.md | head -30
```

## Coverage Note

Initial run found 86 skills vs `skills_list` reporting 91 — 5-skills gap is due to:
- Internal/bundled skills that Hermes loads from the repo's own `skills/` directory
- Skills with non-standard SKILL.md frontmatter
- The `gbrain/setup` alias counted as one file but two entries in the tool
