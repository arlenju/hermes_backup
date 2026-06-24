# Compression Model After Provider Switch

## The Problem

When you switch Hermes from one model/provider to another (e.g., lmstudio/gemma-4-12b → deepseek/deepseek-v4-flash), the **main model** changes immediately for new sessions, but the **auxiliary compression model** may still resolve to the old model.

The config shows `provider: auto` and `model: ''` for `auxiliary.compression`:
```yaml
auxiliary:
  compression:
    provider: auto
    model: ''
```

With `auto` provider, Hermes picks a compression model based on the configured provider chain. If the old provider (e.g., lmstudio) is gone from the config but the auto-resolver hasn't refreshed, it may try to use the old model with an incompatible context window.

## Error Signature

```
ValueError: Auxiliary compression model gemma-4-12b has a context window
of 4,096 tokens, which is below the minimum 64,000 required by Hermes Agent.
Choose a compression model with at least 64K context (set
auxiliary.compression.model in config.yaml), or set
auxiliary.compression.context_length to override the detected value if it
is wrong.
```

This error fires in `agent/conversation_compression.py:check_compression_model_feasibility()` when the detected model's context window is < 64K tokens.

## How to Fix

### Option 1: Restart gateway (clean auto-resolution)

```bash
hermes gateway restart
```

A fresh gateway process re-resolves `auto` providers against the current config, and will pick up the new main provider's model for compression.

### Option 2: Explicitly set compression model

```bash
hermes config set auxiliary.compression.model deepseek-v4-flash
```

Or set any model with ≥ 64K context:
```bash
hermes config set auxiliary.compression.model google/gemma-4-31b-it:free
```

### Option 3: Override context length (for models with known-detected-wrong context)

```bash
hermes config set auxiliary.compression.context_length 131072
```

## Prevention

When switching the main model or provider, always check the auxiliary config afterward:

```bash
grep -A 5 'compression:' ~/.hermes/config.yaml
```

If `model: ''` and `provider: auto`, a gateway restart is recommended to force re-resolution.
