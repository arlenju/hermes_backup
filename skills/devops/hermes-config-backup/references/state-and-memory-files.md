# Hermes Memory & State Files — Complete Inventory

This is the canonical list of files Hermes uses for durable state. A complete backup needs every layer below; missing one means partial restore on disaster recovery.

## Layer 1: Config

| Path | Purpose | Size | Sensitive? |
|------|---------|------|-----------|
| `~/.hermes/config.yaml` | Provider, model, fallback chain, agent settings | ~12K | Yes — `api_key` fields. Sed-redact before commit. |
| `~/.hermes/SOUL.md` | Agent persona/system-prompt seed | <1K | No |
| `~/.hermes/.env` | API keys, app secrets | ~2K | **Never commit.** Read-blocked by Hermes file tool by default. |

## Layer 2: Static Memory (markdown files)

| Path | Purpose | Size |
|------|---------|------|
| `~/.hermes/memories/MEMORY.md` | Agent's notes about environment/conventions | ~3K |
| `~/.hermes/memories/USER.md` | User profile, preferences, communication style | ~3K |

These files are read into the system prompt every turn. They're small, plain markdown, always commit raw.

## Layer 3: Mnemosyne (long-term memory provider)

| Path | Purpose | Size |
|------|---------|------|
| `~/.hermes/mnemosyne/data/mnemosyne.db` | SQLite DB used by the `memory` provider for retrieval-augmented memory | ~1-5M |

This is the one most often overlooked. Mnemosyne is the **memory provider's database** — distinct from the markdown memory files. If it's not backed up, semantic memory recall is lost on restore even if MEMORY.md/USER.md are intact.

The standard backup script copies the entire `mnemosyne/` directory tree:
```bash
cp -R "$HERMES_DIR/mnemosyne/" "$REPO_DIR/mnemosyne/"
```

## Layer 4: Sessions DB (large, compressible)

| Path | Purpose | Size | Compress? |
|------|---------|------|-----------|
| `~/.hermes/state.db` | All chat history, session messages, FTS5 index | 20-100M+ | **Yes** — xz -9 → ~23% |
| `~/.hermes/kanban.db` | Kanban tool state (small) | ~100K | Optional |

state.db grows continuously as the user chats. Without compression it pushes the backup repo size up fast.

**Production-verified compression numbers** (52M state.db, 2026-06-18):
- `xz -k -9` → **12M** (best — ~23%)
- `gzip -9` → 22M (~42%)
- `zip -9` → 22M (~42%)
- bzip2 untested but typically between gzip and xz

xz is the default. Single-file limit on GitHub is 100M; even tenured installs fit.

## Layer 5: Plugins (user-installed extensions)

| Path | Purpose |
|------|---------|
| `~/.hermes/plugins/` | User-installed plugins (each in its own subdir) |

Always commit. Restoring plugins from this directory works as-is — Hermes auto-loads on startup.

## Layer 6: Skills (user-authored procedural memory)

| Path | Purpose |
|------|---------|
| `~/.hermes/skills/` | User-authored skills, organized by category |

The current backup script does **not** copy skills (they're not in `hermes_backup.sh`). The `update_skills_inventory.py` cron generates `SKILLS_INVENTORY.md` (a list, not the content). To back up skill bodies too, add:

```bash
cp -R "$HERMES_DIR/skills/" "$REPO_DIR/skills/" 2>/dev/null
```

This is a gap in the default script — surface it to the user if they want full restore capability.

## Decision tree: what to back up

```
Is it config?       → always commit (redact api_keys)
Is it markdown?     → always commit raw
Is it small SQLite? → commit raw
Is it state.db?     → xz -9, commit .xz
Is it sensitive?    → never commit (.env)
```

## Verification after backup

```bash
# Spot-check files match
diff -q ~/.hermes/config.yaml ~/.hermes_backup_repo/config.yaml
diff -q ~/.hermes/memories/MEMORY.md ~/.hermes_backup_repo/memories/MEMORY.md
diff -q ~/.hermes/mnemosyne/data/mnemosyne.db ~/.hermes_backup_repo/mnemosyne/data/mnemosyne.db
xz -d -c ~/.hermes_backup_repo/state.db.xz | cmp - ~/.hermes/state.db && echo OK
```

If any fail, the backup script has a copy-step bug. Common cause: race with running gateway (state.db locked) — usually safe because SQLite WAL keeps consistent snapshots, but worth knowing.

## When to run a full restore drill

Once a quarter, on a scratch machine:
1. Clone the backup repo
2. Run the restore commands from SKILL.md
3. Start Hermes
4. Confirm: chat history loads, memory recall works, fallback providers work

If any of these fail, the backup is missing something — patch the script.
