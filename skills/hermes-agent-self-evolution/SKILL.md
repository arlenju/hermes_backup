---
name: hermes-agent-self-evolution
description: |-
  Evolutionary self-improvement for Hermes Agent skills using DSPy + GEPA
  (Genetic-Pareto Prompt Evolution). Automatically evolves and optimizes
  SKILL.md files to produce measurably better versions.
version: 1.0.0
tags: [hermes, evolution, optimization, skills, gepa, dspy]
---

# Hermes Agent Self-Evolution

Evolutionary skill optimizer for Hermes Agent. Uses DSPy + GEPA to evolve
skills by mutating text, evaluating results, and selecting the best variants.

**No GPU required.** Everything runs via API calls (~$2-10 per optimization run).

## Prerequisites

- Python env with dependencies: `source ~/My_Project/hermes_agent/Hermes-Agent/venv/bin/activate` (or the venv where `dspy` + `gepa` are installed)
- LLM API key in `~/.hermes/.env` — supported providers: OpenAI (`OPENAI_API_KEY`), DeepSeek (`DEEPSEEK_API_KEY`), Anthropic (`ANTHROPIC_API_KEY`), etc. (see `references/provider-config.md`)

## First-Time Setup

```bash
cd ~/My_Project/hermes_agent/hermes-agent-self-evolution
source ~/My_Project/hermes_agent/Hermes-Agent/venv/bin/activate

# Verify install
python -c "import dspy; import gepa; print('✅ Engines ready')"

# Set which Hermes repo to evolve
export HERMES_AGENT_REPO="$HOME/My_Project/hermes_agent/Hermes-Agent"
```

**⚠️ `HERMES_AGENT_REPO` must be correct.** The code searches `~/.hermes/hermes-agent`
first (standard install). If your repo is elsewhere (e.g. `~/My_Project/hermes_agent/Hermes-Agent`),
it WILL fail with `FileNotFoundError` — set the env var explicitly. Validate:
```bash
ls $HERMES_AGENT_REPO/run_agent.py   # must exist
```

**⚠️ Provider model names use LiteLLM prefixes.** Defaults are OpenAI models.
For non-OpenAI providers you MUST pass `--optimizer-model` and `--eval-model`:
```bash
python -m evolution.skills.evolve_skill \
  --skill <name> \
  --optimizer-model deepseek/deepseek-v4-flash \
  --eval-model deepseek/deepseek-v4-flash
```
See `references/provider-config.md` for all supported providers, the
dry-run validation pattern, and a cost estimate (~$2-10/run).

## Usage

```bash
cd ~/My_Project/hermes_agent/hermes-agent-self-evolution
source ~/My_Project/hermes_agent/Hermes-Agent/venv/bin/activate

# Validate setup without running
python -m evolution.skills.evolve_skill --skill github-code-review --dry-run

# Full evolution with synthetic eval data (cheapest)
python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10 --eval-source synthetic

# Evolve with real session history (most accurate)
python -m evolution.skills.evolve_skill --skill arxiv --iterations 10 --eval-source sessiondb

# With pre-built golden dataset
python -m evolution.skills.evolve_skill --skill arxiv --iterations 10 --eval-source golden --dataset-path datasets/skills/arxiv/

# With test constraints after each iteration
python -m evolution.skills.evolve_skill --skill github-code-review --iterations 10 --run-tests

# Use a different model for the optimizer vs. evaluator
python -m evolution.skills.evolve_skill --skill github-code-review \
  --optimizer-model claude-sonnet-4 --eval-model gpt-4o \
  --iterations 8
```

## How It Works

1. Loads the skill SKILL.md from Hermes skills directory
2. Generates eval dataset (synthetic / golden / session history)
3. GEPA optimizer runs N iterations of: **mutate → evaluate → select best**
4. Constraint gates validate (test suite pass, size limits, semantic preservation)
5. Best variant saved; optional PR generated against hermes-agent repo

## Engines (architecture detail in `references/architecture.md`)

| Engine | Role |
|--------|------|
| **DSPy + GEPA** | Reflective prompt evolution — reads execution traces, proposes targeted mutations (Phase 1-3) |
| **Darwinian Evolver** | Code evolution with Git-based organisms (Phase 4, external CLI) |

## Project Location

```
~/My_Project/hermes_agent/hermes-agent-self-evolution/
```

## References

- `references/deepseek-dspy-setup.md` — Configuring DeepSeek (or other LiteLLM providers) as the optimizer/evaluator model, including API key handling to avoid Hermes tool redaction.
├── evolution/core/                   # Core engine
├── datasets/                         # Eval datasets
├── reports/                          # Generated reports
└── README.md                         # Full docs
```
