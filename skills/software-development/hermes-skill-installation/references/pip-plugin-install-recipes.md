# Hermes Pip Plugin Install Recipes

Concrete install sequences from actual sessions. Keep adding to this file as new community packages are installed.

---

## rtk-hermes v1.2.3 (Terminal Output Compression)

**Source:** [github.com/ogallotti/rtk-hermes](https://github.com/ogallotti/rtk-hermes)
**Type:** Hermes plugin (pre_tool_call hook, rewrites terminal commands)
**Token savings:** 60–90% on common commands (git, ls, pytest, cargo test)

### Install Sequence

```bash
# Step 1 — System binary
brew install rtk
rtk --version                                       # verify: 0.42.4+
rtk rewrite "git status"                           # verify it works

# Step 2 — Plugin into Hermes venv
~/.hermes/hermes-agent/venv/bin/pip install --upgrade rtk-hermes
~/.hermes/hermes-agent/venv/bin/pip show rtk-hermes  # verify: 1.2.3

# Step 3 — Enable in config
hermes config set plugins.enabled '["rtk-rewrite"]'

# Step 4 — Restart gateway
hermes gateway restart
```

### Config Check

```yaml
# ~/.hermes/config.yaml should have:
plugins:
  enabled:
    - rtk-rewrite
```

### Runtime Env (optional)

```bash
export RTK_HERMES_MODE=rewrite          # rewrite, suggest, or off
export RTK_HERMES_TIMEOUT_MS=2000       # max ms per call
export RTK_HERMES_PREVIEW_MARKER=true   # show ": RTK &&" prefix
export RTK_HERMES_BACKENDS=local        # backends to rewrite on
```

### Upgrade

```bash
brew upgrade rtk
~/.hermes/hermes-agent/venv/bin/pip install --upgrade rtk-hermes
hermes gateway restart
```

---

## Mnemosyne v0.2.0 (Memory Provider)

**Source:** [github.com/AxDSan/Mnemosyne](https://github.com/AxDSan/Mnemosyne)
**Type:** Hermes memory provider (replaces built-in memory with SQLite+vec+FTS5 hybrid)
**Benchmarks:** 98.9% LongMemEval recall, 65.2% BEAM 100K QA, 9.4x storage compression
**Tools exposed:** 23 tools across 5 categories (Core, Knowledge Graph, Multi-agent Surface, Working Notes, Ops)

### Install Sequence

```bash
# Step 1 — Package into Hermes venv
~/.hermes/hermes-agent/venv/bin/pip install --upgrade mnemosyne-hermes
~/.hermes/hermes-agent/venv/bin/pip show mnemosyne-hermes  # verify: 0.2.0

# Step 2 — Set memory provider
hermes config set memory.provider mnemosyne

# Step 3 — Disable built-in memory (after confirming install worked)
hermes config set memory.memory_enabled false
hermes config set memory.user_profile_enabled false

# Step 4 — (Optional, for Chinese) Set embedding model
#     In ~/.hermes/.env or gateway env:
#     MNEMOSYNE_EMBEDDING_MODEL=BAAI/bge-small-zh-v1.5

# Step 5 — Restart gateway
hermes gateway restart
```

### Config Check

```yaml
# ~/.hermes/config.yaml should have:
memory:
  memory_enabled: false
  user_profile_enabled: false
  write_approval: false
  memory_char_limit: 2200
  user_char_limit: 1375
  provider: mnemosyne
```

### CLI Commands (if supported by version)

```
hermes memory setup         # initialize Mnemosyne DB
hermes mnemosyne stats      # show memory statistics
```

### Upgrade

```bash
~/.hermes/hermes-agent/venv/bin/pip install --upgrade mnemosyne-hermes
hermes gateway restart
```

### Rollback (restore built-in memory)

```bash
hermes config set memory.memory_enabled true
hermes config set memory.user_profile_enabled true
hermes config set memory.provider ""          # empty = use built-in
hermes gateway restart
```

---

## Hindsight (Cloud Memory Provider)

**Source:** [github.com/vectorize-io/hindsight](https://github.com/vectorize-io/hindsight)
**Type:** Hermes memory provider (cloud-based, requires API key)
**Note:** This is a **cloud service** — memory operations make API calls to vectorize.io. Not local/offline.

### Install Sequence

```bash
# Step 1 — Run the interactive setup wizard
hermes memory setup hindsight

# The wizard will:
#   - Auto-install hindsight-client Python package
#   - Prompt for API key (get from https://ui.hindsight.vectorize.io)
#   - Prompt for API URL (default: https://api.hindsight.vectorize.io)
#   - Write config to ~/.hermes/config.yaml
```

### Prerequisites

- **API key** required — register at [ui.hindsight.vectorize.io](https://ui.hindsight.vectorize.io)
- The wizard is **interactive** (reads from stdin). In non-interactive environments (WeChat, Feishu), you cannot complete the setup. The user must run it in a terminal directly.

### Manual Config (if wizard unavailable)

If the wizard can't run interactively, the config can be set manually:

```yaml
# ~/.hermes/config.yaml
memory:
  provider: hindsight
  hindsight:
    api_key: "your-api-key-here"
    api_url: "https://api.hindsight.vectorize.io"
  memory_enabled: false
  user_profile_enabled: false
```

### Rollback

```bash
hermes config set memory.provider ""
hermes config set memory.memory_enabled true
hermes config set memory.user_profile_enabled true
hermes gateway restart
```

---

## Pattern Summary

| Package | System Dep | Pip Target | Config Change | Restart Needed | Interactive? |
|---------|-----------|------------|---------------|----------------|--------------|
| rtk-hermes | `brew install rtk` | Hermes venv | `plugins.enabled` | Yes | No |
| mnemosyne-hermes | None | Hermes venv | `memory.provider` + disable built-in | Yes | No |
| hindsight | None (auto-installed by wizard) | Hermes venv | `memory.provider` + API key | Yes | Yes (wizard) |

All install into `~/.hermes/hermes-agent/venv/` — the **Hermes runtime venv**, NOT the system Python and NOT the project dev venv.

**Key distinction:** Mnemosyne is local/offline (SQLite, zero cost). Hindsight is cloud-based (API calls, requires key). Choose based on whether the user wants local-first or cloud-backed memory.
