# Agent Reach — Install Recipe (verified macOS, June 2026)

[Agent Reach](https://github.com/Panniantong/Agent-Reach) is the canonical example of the
"multi-agent-aware CLI tool + SKILL.md" pattern (see SKILL.md §6).
It's a **capability layer** that gives any agent free internet access across
13 platforms (Twitter, Reddit, B站, 小红书, YouTube, GitHub, RSS, Exa, V2EX,
LinkedIn, 雪球, 小宇宙, Web). Multi-backend routing — when one upstream
breaks, the project switches to the next.

**It is NOT a Hermes plugin and NOT a memory provider.** It's a standalone
`pipx` CLI plus a SKILL.md that teaches agents which upstream tool to call.

## Install steps (verified June 2026, Agent Reach 1.5.0, macOS Tahoe)

```bash
# 1. Prereqs check
python3 --version       # ≥ 3.10
which gh node           # both should resolve
which brew              # for pipx install

# 2. Bootstrap pipx (Homebrew Python hits PEP 668 with raw pip)
brew install pipx

# 3. Make ~/.local/bin available
export PATH="$HOME/.local/bin:$PATH"

# 4. Install agent-reach itself
pipx install https://github.com/Panniantong/agent-reach/archive/main.zip
# → installed package agent-reach 1.5.0
# → /Users/<user>/.local/bin/agent-reach

# 5. Run the installer (zero-config channels)
agent-reach install --env=auto
# Activates 5 zero-config channels by default:
#   ✅ Web (Jina Reader)
#   ✅ YouTube (yt-dlp)        ← may need step 6 if missing
#   ✅ RSS (feedparser)
#   ✅ Exa Search (mcporter)
#   ✅ Bilibili (search-only)

# 6. (If YouTube shows ❌)  Install yt-dlp globally
pipx install yt-dlp

# 7. Mirror SKILL.md into Hermes
mkdir -p ~/.hermes/skills/research/agent-reach
cp -r ~/.claude/skills/agent-reach/* ~/.hermes/skills/research/agent-reach/

# 8. Reload skills in the running session
# In Hermes CLI: /reload-skills
# Or start a fresh session.

# 9. Verify
agent-reach doctor    # Reports channel statuses + active backend per platform
```

## Optional channels (need credentials / extra setup)

```bash
agent-reach install --env=auto --channels=opencli,xiaohongshu  # XHS via OpenCLI
agent-reach install --env=auto --channels=twitter              # Twitter (needs cookie)
agent-reach install --env=auto --channels=all                  # everything
```

Cookie-based channels (Twitter, 小红书, 雪球) need user-side action — the
agent should NEVER drive a login flow in its own browser. Pattern: tell
the user to install the [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
Chrome extension, log in, export "Header String", paste it back. Then:

```bash
agent-reach configure twitter-cookies "PASTED_STRING"
```

This is the same handoff pattern documented in the `model-fallback`
skill's `references/credential-handoff-pattern.md` — defer to that.

## Daily reading commands (after install)

| Task | Command |
|------|---------|
| Read web page | `curl -s https://r.jina.ai/<URL>` |
| YouTube subs | `yt-dlp --write-auto-sub --skip-download <URL>` |
| RSS feed | `python3 -c "import feedparser; ..."` |
| Exa search | `mcporter call 'exa.web_search_exa(...)'` |
| GitHub | `gh repo view owner/repo` (after `gh auth login`) |
| B站 search | `bili search "query" --type video` |

The agent reads the mirrored SKILL.md and dispatches to the right CLI
automatically — no need to memorize.

## Common install issues

1. **`pipx: command not found`** — install via `brew install pipx` on
   macOS, `apt install pipx` on Debian/Ubuntu, then `pipx ensurepath`.
2. **`externally-managed-environment` from `pip install`** — PEP 668.
   Use `pipx` (correct) or `python3 -m venv ~/.agent-reach-venv` (also
   fine). NEVER `pip install --break-system-packages`.
3. **`yt-dlp` reported as missing** even though core install succeeded —
   the `--env=auto` installer doesn't always install yt-dlp itself.
   Run `pipx install yt-dlp` separately.
4. **V2EX shows ❌ `IncompleteRead(0 bytes read)`** — V2EX API is flaky
   from outside China, sometimes rate-limits, sometimes plain blocks.
   Set proxy via `agent-reach configure proxy http://...` if needed.
   Not a fatal install error.
5. **GitHub shows ⚠️ "gh CLI installed but not authenticated"** — public
   repos work without auth via `gh search repos`. For private / issues /
   PRs, run `gh auth login`. The user makes the choice.
6. **SKILL.md doesn't appear in `skill_view`** — you forgot to mirror it
   to `~/.hermes/skills/`. Run step 7 above.

## Update / uninstall

```bash
# Update (the SKILL.md update doc tells the agent how to do this)
# Tell the agent: "帮我更新 Agent Reach: <update.md URL>"

# Uninstall everything
agent-reach uninstall              # removes ~/.agent-reach/, MCP configs, mirrored skills
pip uninstall agent-reach          # remove the Python package itself
```

## See also

- Project repo: https://github.com/Panniantong/Agent-Reach
- Install doc (the canonical instruction the user pastes to their agent):
  https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md
- `model-fallback` skill, `references/credential-handoff-pattern.md` —
  for the cookie/Twitter credential handoff
