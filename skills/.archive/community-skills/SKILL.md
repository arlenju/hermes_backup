---
name: community-skills
category: software-development
description: >-
  Discover, evaluate, and install community Hermes skills from GitHub repos,
  Hermes Atlas, and other sources — especially multi-file installs with
  SKILL.md + plugins + templates + prisms.
version: 1.0.0
tags: [hermes, skills, community, atlas, git]
---

# Community Skills — Discover & Install from GitHub Repos

> When a skill isn't on the hub, install it from a community GitHub repo.

## When to Use

- User asks to install a skill from Hermes Atlas (hermesatlas.com)
- User found a skill on GitHub that isn't on the hub
- Skill repo has a `skills/` subdirectory, `plugins/`, `templates/`, or `prisms/`
- Repo has an `install.sh` script for multi-file installation

## Workflow

### Phase 1: Discover & Inspect the Repo

Check the GitHub repo structure:

```bash
# Default branch (not always 'main')
curl -s "https://api.github.com/repos/<owner>/<repo>" | python3 -c \
  "import sys,json; print(json.load(sys.stdin).get('default_branch','main'))"
```

Check what's at the root:
```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/contents/" | python3 -c \
  "import sys,json; [print(i['name'], i['type']) for i in json.load(sys.stdin)]"
```

**Look for these key files:**
- `SKILL.md` at root — single-file skill
- `skills/<name>/SKILL.md` — skill in subdirectory
- `install.sh` — automated install script
- `plugins/` — Python plugin files
- `prisms/` — analytical templates (super-hermes pattern)
- `templates/` — boilerplate templates
- `README.md` — install instructions

### Phase 2: Choose Install Method

#### A) Has `install.sh` (easiest)

Clone and run:
```bash
git clone https://github.com/<owner>/<repo>.git /tmp/<repo>
cd /tmp/<repo>
bash install.sh
```

**Verify:**
```bash
hermes skills reload
skill_view(name='<skill-name>')
```

#### B) Manual multi-file copy (no install.sh)

For repos structured like `hermes-skill-factory` or `super-hermes`:

```bash
# Skills in subdirectory
for skill in skill-a skill-b; do
  mkdir -p ~/.hermes/skills/$skill
  curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/skills/$skill/SKILL.md" \
    -o ~/.hermes/skills/$skill/SKILL.md
done

# Plugins
mkdir -p ~/.hermes/plugins
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/plugins/<name>.py" \
  -o ~/.hermes/plugins/<name>.py

# Prisms/templates
mkdir -p ~/.hermes/prisms
for prism in prism-a prism-b; do
  curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/prisms/$prism.md" \
    -o ~/.hermes/prisms/$prism.md
done
```

#### C) Single SKILL.md (simple)

```bash
mkdir -p ~/.hermes/skills/<name>
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/<branch>/SKILL.md" \
  -o ~/.hermes/skills/<name>/SKILL.md
```

#### D) Hub install (when available)

```bash
yes | hermes skills install <identifier>
```

### Phase 3: Verify

```bash
ls ~/.hermes/skills/ | grep <skill>
ls ~/.hermes/plugins/   # for plugins
skill_view(name='<skill>')
```

### Phase 4: Skill Reload

Newly installed skills take effect after:
- `/reset` in current session
- Full `hermes` restart
- Some hubs do `/reload-skills`

## Hermes Atlas (hermesatlas.com)

**Community skill map** — lists 160+ tools, skills, plugins.

Use the **browser** tool to browse:
```
https://hermesatlas.com/lists/top-skills    — ranked by stars
https://hermesatlas.com/                    — full map by category
```

Popular community categories:
- **Skills & skill registries** — individual reusable skills
- **Workspaces & GUIs** — web/desktop interfaces for Hermes
- **Core & official** — NousResearch official projects
- **Multi-agent frameworks** — swarm, fleet coordination

## Common Repo Structures

### Structure A: Skill Factory pattern
```
repo/
├── skills/<name>/SKILL.md     ← the skill file
├── plugins/<name>.py           ← slash commands
├── templates/                  ← generation templates
├── install.sh                  ← auto-installer
```

### Structure B: Prism pattern (super-hermes)
```
repo/
├── skills/prism-*/SKILL.md     ← multiple standalone skills
├── prisms/<name>.md            ← analytical templates
├── examples/                   ← usage demos
├── install.sh                  ← auto-installer
```

### Structure C: Flat skill
```
repo/
├── SKILL.md                    ← single skill at root
```

## Pitfalls

1. **Branch is not always `main`.** Some repos use `master`. Check via API.
2. **SKILL.md not at root.** Check `skills/<name>/SKILL.md` path.
3. **install.sh fails mid-way.** Scripts may assume Hermes is freshly installed. Run step-by-step manually instead.
4. **Plugin needs Hermes v2026.3+.** Check the README for version requirements.
5. **Skills appear in `ls` but `skill_view` fails.** Missing or malformed YAML frontmatter — validate `---` markers.
6. **Security scanner blocks community skills.** Manual copy to `~/.hermes/skills/` bypasses the hub scan entirely — only do this for repos you trust.
7. **no_agent cron for script-only jobs.** When setting up cron for a Python/bash script without LLM, use `no_agent=True` — zero token cost.

## References

- `hermes-skill-installation` — hub install and single-file methods
- `hermes-config-backup` — backup scripts and cron patterns
- [Hermes Atlas](https://hermesatlas.com) — community skill map
