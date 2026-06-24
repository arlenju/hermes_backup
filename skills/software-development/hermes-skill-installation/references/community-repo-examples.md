# Community Repo Install Examples

Worked examples from actual installs on this machine.

---

## hermes-skill-factory

**Repo:** `Romanescu11/hermes-skill-factory` (★353, Atlas #7)
**Branch:** `master`
**Description:** Meta-skill that watches your workflows and auto-generates reusable skills.

### File Layout

```
hermes-skill-factory/
├── skills/skill-factory/SKILL.md    → ~/.hermes/skills/meta/skill-factory/
├── plugins/skill_factory.py         → ~/.hermes/plugins/
├── install.sh                       # Clone + run this
├── templates/                       # Templates for generated skills
└── README.md
```

### Manual Install (no clone)

```bash
# SKILL.md
mkdir -p ~/.hermes/skills/meta/skill-factory
curl -sL "https://raw.githubusercontent.com/Romanescu11/hermes-skill-factory/master/skills/skill-factory/SKILL.md" \
  -o ~/.hermes/skills/meta/skill-factory/SKILL.md

# Plugin
mkdir -p ~/.hermes/plugins
curl -sL "https://raw.githubusercontent.com/Romanescu11/hermes-skill-factory/master/plugins/skill_factory.py" \
  -o ~/.hermes/plugins/skill_factory.py
```

### Commands

| Command | Description |
|---------|-------------|
| `/skill-factory propose` | Analyze session, propose top skill now |
| `/skill-factory list` | List skills generated this session |
| `/skill-factory status` | Show tracked patterns |
| `/skill-factory save <name>` | Save last proposal with custom name |

---

## super-hermes (Prism Skills)

**Repo:** `Cranot/super-hermes` (★211, Atlas #11)
**Branch:** `master`
**Description:** 5 analytical prisms + 7 proven lenses for deep code analysis.

### File Layout

```
super-hermes/
├── skills/prism-scan/SKILL.md          → ~/.hermes/skills/prism-scan/
├── skills/prism-full/SKILL.md          → ~/.hermes/skills/prism-full/
├── skills/prism-3way/SKILL.md          → ~/.hermes/skills/prism-3way/
├── skills/prism-discover/SKILL.md      → ~/.hermes/skills/prism-discover/
├── skills/prism-reflect/SKILL.md       → ~/.hermes/skills/prism-reflect/
├── prisms/error_resilience.md          → ~/.hermes/prisms/
├── prisms/l12.md                       → ~/.hermes/prisms/
├── prisms/optimize.md                  → ~/.hermes/prisms/
├── prisms/identity.md                  → ~/.hermes/prisms/
├── prisms/deep_scan.md                 → ~/.hermes/prisms/
├── prisms/claim.md                     → ~/.hermes/prisms/
├── prisms/simulation.md                → ~/.hermes/prisms/
├── install.sh                          # Clone + run this
└── examples/                           # Demo outputs
```

### Manual Install (no clone)

```bash
# 5 skills
for skill in prism-scan prism-full prism-3way prism-discover prism-reflect; do
  mkdir -p ~/.hermes/skills/$skill
  curl -sL "https://raw.githubusercontent.com/Cranot/super-hermes/master/skills/$skill/SKILL.md" \
    -o ~/.hermes/skills/$skill/SKILL.md
done

# 7 prisms
for prism in error_resilience l12 optimize identity deep_scan claim simulation; do
  curl -sL "https://raw.githubusercontent.com/Cranot/super-hermes/master/prisms/$prism.md" \
    -o ~/.hermes/prisms/$prism.md
done
```

### Commands

| Command | Description |
|---------|-------------|
| `/prism-scan` | Dynamic lens generation + structural analysis |
| `/prism-full` | Multi-pass pipeline with adversarial self-correction |
| `/prism-3way` | WHERE/WHEN/WHY three-angle analysis + synthesis |
| `/prism-discover` | Map all possible analysis domains |
| `/prism-reflect` | Self-aware analysis + constraint transparency report |

### Prisms (standalone use as system prompts)

| File | Focus | Score |
|------|-------|-------|
| `error_resilience.md` | Corruption cascades, silent exits | 10.0 |
| `l12.md` | Conservation laws, meta-laws | 9.8 |
| `optimize.md` | Critical path tracing | 9.5 |
| `identity.md` | Claims vs reality | 9.5 |
| `deep_scan.md` | Information destruction, laundering | 9.0 |
| `claim.md` | Assumption inversion | 9.0 |
| `simulation.md` | Temporal prediction | 9.0 |

---

## obsidian-skills (OpenCode / Agent Skills spec → Hermes)

**Repo:** `kepano/obsidian-skills` (★35.8k)
**Branch:** `main`
**Description:** Agent skills for Obsidian — teaches agents to use Obsidian Flavored Markdown, Bases, JSON Canvas, CLI, and Defuddle.

This is an **OpenCode/Agent Skills spec** repo, not a Hermes-native one. The SKILL.md format is identical and directly compatible.

### File Layout

```
obsidian-skills/
├── skills/
│   ├── obsidian-markdown/SKILL.md    → ~/.hermes/skills/obsidian/obsidian-markdown/
│   ├── obsidian-bases/SKILL.md       → ~/.hermes/skills/obsidian/obsidian-bases/
│   ├── obsidian-cli/SKILL.md         → ~/.hermes/skills/obsidian/obsidian-cli/
│   ├── json-canvas/SKILL.md          → ~/.hermes/skills/obsidian/json-canvas/
│   └── defuddle/SKILL.md             → ~/.hermes/skills/obsidian/defuddle/
└── README.md
```

### Manual Install

Grouped under a semantic category directory to avoid name collisions:

```bash
for skill in obsidian-markdown obsidian-bases obsidian-cli json-canvas defuddle; do
  mkdir -p ~/.hermes/skills/obsidian/$skill
  curl -sL "https://raw.githubusercontent.com/kepano/obsidian-skills/main/skills/$skill/SKILL.md" \
    -o ~/.hermes/skills/obsidian/$skill/SKILL.md
done
```

### Verification

```bash
skills_list() | grep obsidian
# Should show 5 skills under "obsidian" category
skill_view(name="obsidian/obsidian-markdown")  # loads successfully
```

### Skills Reference

| Skill | Usage |
|-------|-------|
| `obsidian-markdown` | Write Obsidian Flavored Markdown (wikilinks, callouts, embeds, properties) |
| `obsidian-bases` | Create/edit database-like views (.base files) in Obsidian |
| `obsidian-cli` | Interact with a running Obsidian instance via CLI |
| `json-canvas` | Create mind maps/flowcharts as .canvas files |
| `defuddle` | Extract clean markdown from web pages (requires `npm install -g defuddle`) |

### Key Differences from Hermes-Native Repos

- Uses `main` branch (most Hermes community repos use `master`)
- No plugins or prisms — pure SKILL.md files
- Follows OpenCode directory layout (`skills/<name>/SKILL.md`)
- Skills work with any agent that supports the Agent Skills spec (Claude Code, Codex, OpenCode, Hermes)
- `obsidian-cli` and `defuddle` require external CLI tools to be pre-installed

---

## Atlas Comparison Pattern

When the user asks "which top skills aren't installed yet":

1. `skills_list()` → get all local skills (names + descriptions)
2. Browser to `hermesatlas.com/lists/top-skills` → get ranked community skills
3. For each Atlas entry, check for a local match by:
   - Exact name match
   - Semantic similarity (e.g. `humanizer` ≈ `avoid-ai-writing`)
   - Functional overlap (e.g. `architecture-diagram`/`excalidraw` ≈ `drawio-skill`)
4. Report: ✅ already covered / ❌ not installed
