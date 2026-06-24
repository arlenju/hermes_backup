---
name: codebase-inspection
description: "Comprehensive project quality review: LOC, architecture, tooling, tests, dependencies, git state, and config audit."
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LOC, Code Analysis, pygount, Codebase, Metrics, Repository, Quality, Review, Architecture]
    related_skills: [github-repo-management, github-code-review]
prerequisites:
  commands: [pygount]
---

# Codebase Inspection — Comprehensive Project Quality Review

Analyze a software project holistically: lines of code, language breakdown, quality tooling, test coverage, dependencies, architecture, git state, and configuration hygiene. This skill covers both a quick LOC count and a full multi-dimensional project audit.

## When to Use

- User asks "check this project" or "review this codebase"
- User wants LOC count, language breakdown, or codebase size
- User asks about code quality, test coverage, or project maturity
- User wants a "health check" on a repo before contributing
- User wants architecture overview and dependency analysis

## Quick LOC Count

If the user only wants a quick size/language breakdown, use pygount (see § pygount below).

## Full Project Review — Multi-Dimensional Audit

When the user says "check this project" or similar, perform ALL of the following dimensions. Read the key files directly (not via pygount) to get qualitative insight.

### 1. Project Metadata & Dependencies

Read `pyproject.toml` (or `setup.py`/`setup.cfg`/`package.json`/`Cargo.toml`):
- Project name, version, author, license
- Python version requirement / minimum engine version
- Core dependencies vs optional/extras dependencies
- Build system (setuptools, poetry, uv, maturin, etc.)
- Links: homepage, repo, docs, changelog

### 2. Quality Tooling Configuration

Read the following files if present:

| File | What to check |
|------|--------------|
| `ruff.toml` / `.ruff.toml` / `.flake8` | Linter rules, line length, target version, ignored rules |
| `pytest.ini` / `pyproject.toml [tool.pytest]` | Test config: asyncio mode, markers, plugins, verbosity |
| `tox.ini` | Multi-env testing, Python version matrix, test command strategy |
| `.pre-commit-config.yaml` | Pre-commit hooks: ruff, bandit, mypy, vermin, etc. |
| `.bandit.yml` / similar | Security scanning configuration |
| `mypy.ini` / `pyproject.toml [tool.mypy]` | Type checker strictness |
| `pyrightconfig.json` / `pyproject.toml [tool.pyright]` | Microsoft Pyright configuration |
| `.github/workflows/` | CI pipeline: test matrix, deployment, Docker build |

### 3. Source Tree & Architecture

Navigate the source tree to understand the architecture:
- Use `find` to list source files by category
- Count lines per major module: `wc -l scrapling/*.py scrapling/**/*.py`
- Identify the core abstraction(s) and how modules relate
- Note: lazy imports, __init__.py re-exports, plugin systems

### 4. Test Coverage Assessment

Read test directory structure and test config:
- Count test files and total test lines: `find tests -name "*.py" | xargs wc -l`
- Examine pytest markers and test categories
- Check if tests cover: unit, integration, async, browser, CLI
- Note CI test matrix coverage

### 5. Git Activity

```bash
# Recent commits
git log --oneline -10

# Current branch state
git branch -a

# Working tree cleanliness
git status --short

# Latest tag
git describe --tags --abbrev=0
```

### 6. Docker & Deployment

Read `Dockerfile` if present:
- Base image choice (slim vs full, multi-stage?)
- Dependency caching strategy
- Entrypoint and default command

### 7. Project Boundary Files

Check these for completeness:
- `README.md` — quality of docs, examples, badges
- `CONTRIBUTING.md` — contribution guidelines
- `CODE_OF_CONDUCT.md`
- `LICENSE` — license type
- `CHANGELOG.md` / `ROADMAP.md`
- `.gitignore` — what's excluded
- `MANIFEST.in` — what's included in package distribution

### 8. Produce a Structured Report

Organize findings into a table-driven report with these sections:

```
### 📋 Basic Info
| Field | Value |
|-------|-------|
| Name/Version | ... |
| Author | ... |
| License | ... |
| Python min | ... |
| Total LOC | ... (source + tests) |

### 🏗️ Architecture
- Key modules and their responsibilities
- Design patterns used
- Notable implementation details

### ✅ Quality Assessment
| Dimension | Status |
|-----------|--------|
| Type hints | ✅ Full / ⚠️ Partial / ❌ None |
| Linter | ruff/flake8/pylint + config |
| Formatter | black/ruff ... |
| Type checker | mypy/pyright/both |
| Security scanner | bandit/semgrep/... |
| Pre-commit | ✅ configured / ❌ missing |
| Tests | pytest/unittest + framework details |
| CI | GitHub Actions/GitLab/Jenkins |
| Docker | multi-stage / single / ❌ none |

### ⚠️ Observations
- Strengths
- Potential concerns
- Notable patterns
- Outdated/derived/copied code
```

## pygount (LOC & Language Breakdown)

Analyze repositories for lines of code, language breakdown, file counts, and code-vs-comment ratios.

### Prerequisites

```bash
pip install --break-system-packages pygount 2>/dev/null || pip install pygount
```

### 1. Basic Summary

```bash
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,.eggs,*.egg-info" \
  .
```

**IMPORTANT:** Always use `--folders-to-skip` to exclude dependency/build directories, otherwise pygount will crawl them and take a very long time or hang.

### 2. Common Folder Exclusions

```bash
# Python projects
--folders-to-skip=".git,venv,.venv,__pycache__,.cache,dist,build,.tox,.eggs,.mypy_cache"

# JavaScript/TypeScript projects
--folders-to-skip=".git,node_modules,dist,build,.next,.cache,.turbo,coverage"

# General catch-all
--folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build,.next,.tox,vendor,third_party"
```

### 3. Filter by Specific Language

```bash
pygount --suffix=py --format=summary .
pygount --suffix=py,yaml,yml --format=summary .
```

### 4. Detailed File-by-File Output

```bash
pygount --folders-to-skip=".git,node_modules,venv" . | sort -t$'\t' -k1 -nr | head -20
```

### 5. Output Formats

```bash
pygount --format=summary .        # Summary table (default recommendation)
pygount --format=json .            # JSON output for programmatic use
```

### 6. Interpreting Results

Summary columns: Language, Files, Code, Comment, %. Special pseudo-languages: `__empty__`, `__binary__`, `__generated__`, `__duplicate__`, `__unknown__`.

## Pitfalls

1. **Always exclude .git, node_modules, venv** — without `--folders-to-skip`, pygount crawls everything and may hang.
2. **Markdown shows 0 code lines** — pygount classifies Markdown as comments, not code. Expected.
3. **JSON files show low code counts** — use `wc -l` directly for accurate JSON counts.
4. **Large monorepos** — use `--suffix` to target specific languages rather than scanning everything.
5. **Don't confuse `pygount --format=summary` with a full quality review** — LOC is one dimension. Always do the qualitative file-reading pass for a real project check.
6. **`setup.cfg` often duplicates `pyproject.toml`** — in migrated Python projects, `setup.cfg` is often a stale leftover. Flag this if you see both.
7. **Always check git status** — a project may look clean from files alone but have uncommitted changes, untracked files, or be on a stale branch.
