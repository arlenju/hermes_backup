# Provider Model Configuration for GEPA/DSPy

## LiteLLM Provider Prefixes

GEPA uses LiteLLM internally. Pass model names as `<provider>/<model>`:

| Provider | Prefix | Env Var | Example |
|----------|--------|---------|---------|
| OpenAI | `openai/` | `OPENAI_API_KEY` | `openai/gpt-4o` |
| DeepSeek | `deepseek/` | `DEEPSEEK_API_KEY` | `deepseek/deepseek-v4-flash` |
| Anthropic | `anthropic/` | `ANTHROPIC_API_KEY` | `anthropic/claude-sonnet-4` |
| Groq | `groq/` | `GROQ_API_KEY` | `groq/llama-3.3-70b` |
| Together | `together_ai/` | `TOGETHER_API_KEY` | `together_ai/mixtral-8x22b` |

## CLI Override Flags

```bash
--optimizer-model <model>    # Model for GEPA reflections (mutations)
--eval-model <model>         # Model for LLM-as-judge scoring
```

Both default to OpenAI models. Override both when using a non-OpenAI provider.

## Dry-Run Validation Pattern

Always run a dry-run first to validate setup before spending API credits:

```bash
export HERMES_AGENT_REPO="$HOME/My_Project/hermes_agent/Hermes-Agent"
python -m evolution.skills.evolve_skill \
  --skill github-code-review \
  --optimizer-model deepseek/deepseek-v4-flash \
  --eval-model deepseek/deepseek-v4-flash \
  --dry-run
```

**Expected output on success:**

```
🧬 Hermes Agent Self-Evolution — Evolving skill: github-code-review

  Loaded: skills/github/github-code-review/SKILL.md
  Name: github-code-review
  Size: 13,481 chars
  Description: Review PRs: diffs, inline comments via gh or REST....

DRY RUN — setup validated successfully.
  Would generate eval dataset (source: synthetic)
  Would run GEPA optimization (10 iterations)
  Would validate constraints and create PR
```

If you see `FileNotFoundError: Cannot find hermes-agent repo`, the
`HERMES_AGENT_REPO` env var is pointing to the wrong path. Verify with
`ls $HERMES_AGENT_REPO/run_agent.py`.

## DeepSeek Compatibility (verified)

DeepSeek models work with GEPA/DSPy via LiteLLM's `deepseek/` prefix.
Tested with `deepseek/deepseek-v4-flash` for both optimizer and eval roles.
Dry-run validation passed. Cost is significantly lower than GPT-4.

## Cost Estimate

~$2-10 per optimization run depending on:
- Model used (DeepSeek is cheaper than GPT-4)
- Iteration count (default 10)
- Population size (default 5)
- Eval dataset size (default 20 examples)
