# Hermes Memory System Audit Guide

When a user asks about memory sync status or memory seems unavailable, use this
guide to systematically inspect the three layers of the Hermes memory system.

## Layer 1: Config (the Switch)

Check `~/.hermes/config.yaml`:

```yaml
memory:
  memory_enabled: false
  user_profile_enabled: false
```

- Both must be `true` for the `memory` tool to be available at runtime.
- The `provider` field (e.g. `mnemosyne`) controls the backend.
- When `memory_enabled: false`, the `memory` tool returns "Memory is not
  available" even if the Mnemosyne DB has data.

## Layer 2: Old-Style File Memory (the Files)

Legacy memory is stored in `~/.hermes/memories/`:

| File | Purpose |
|------|---------|
| `USER.md` | User profile entries, `§`-separated |
| `MEMORY.md` | Episodic/technical memory entries, `§`-separated |

When `memory_enabled: false`, these files are still read and injected into the
system prompt on every turn (they serve as the fallback mechanism). Each `§`
separator delineates a distinct entry.

**Diagnostic command:**
```bash
ls -la ~/.hermes/memories/
# Expected: USER.md, MEMORY.md, plus .lock files
```

**Check content parity with Mnemosyne:**
```python
# Count entries in old files
grep -c '§' ~/.hermes/memories/USER.md
grep -c '§' ~/.hermes/memories/MEMORY.md

# Compare with Mnemosyne
python3 -c "
import sys; sys.path.insert(0, '$HOME/.hermes/hermes-agent/venv/lib/python3.11/site-packages')
from mnemosyne import recall
epi = recall('hermes_memory')
pro = recall('hermes_user_profile')
print(f'Episodic: {len(epi) if isinstance(epi, list) else epi}')
print(f'Profile:   {len(pro) if isinstance(pro, list) else pro}')
"
```

## Layer 3: Mnemosyne Database (the DB)

The provider backend lives at `~/.hermes/mnemosyne/data/mnemosyne.db`.

**Diagnostic:**
```bash
ls -lh ~/.hermes/mnemosyne/data/mnemosyne.db
# Expected: ~1MB for typical usage. 0 bytes = never populated.
```

**Migration script** at `~/.hermes/scripts/migrate_memory_to_mnemosyne.py`
reads old-style `USER.md`/`MEMORY.md` files and writes each `§`-separated
entry into the Mnemosyne DB under two scopes:
- `hermes_memory` (importance=0.8)
- `hermes_user_profile` (importance=0.9)

**When migration was run but memory is still unavailable:**
The migration creates the DB and populates it, but `memory.memory_enabled` and
`memory.user_profile_enabled` in `config.yaml` stay `false`. You must enable
both in config, then the `memory` tool appears on next session.

## Backup Interaction

The backup script (`~/.hermes_backup_repo`) backs up both layers:

```bash
# Old files — always backed up
cp "$HERMES_DIR/memories/USER.md" "$REPO_DIR/memories/USER.md"
cp "$HERMES_DIR/memories/MEMORY.md" "$REPO_DIR/memories/MEMORY.md"

# Mnemosyne DB — backed up if directory exists
cp -R "$HERMES_DIR/mnemosyne/" "$REPO_DIR/mnemosyne/"
```

**Known timing gap:** If the Mnemosyne DB is created after the last backup
(e.g. midnight backup ran at 00:00, Mnemosyne DB created at 10:00), the
database is NOT in the backup repo until the next scheduled run. Trigger an
immediate backup to close the gap:

```bash
cd ~/.hermes_backup_repo && \
  cp -R ~/.hermes/mnemosyne/ ./mnemosyne/ && \
  git add -A && git commit -m "manual mnemosyne backup $(date)" && git push
```

## Quick-Reference Decision Tree

```
User asks "memory synced?"
├─ Check config: memory_enabled?
│  ├─ false → memory tool unavailable. Old files still used.
│  └─ true  → memory tool active. Check DB health.
├─ Check Mnemosyne DB exists + has data?
│  ├─ No → migration script never ran or failed. Run it.
│  └─ Yes → compare entry count vs old files.
├─ Check GitHub backup?
│  ├─ cron job active? (cronjob action=list)
│  ├─ last backup time? (git log -1 in ~/.hermes_backup_repo)
│  └─ Mnemosyne DB in backup? (ls ~/.hermes_backup_repo/mnemosyne/)
└─ Report: what IS synced, what is NOT, and what to fix.
```
