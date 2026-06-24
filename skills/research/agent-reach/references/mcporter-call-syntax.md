# mcporter call syntax + Twitter fallback when no cookie

Two non-obvious gotchas discovered while using Agent Reach on a clean install.

## 1. `mcporter call` does NOT accept function-style arguments

This **fails**:

```bash
mcporter call 'exa.web_search_exa(query="trending topics", numResults=10)'
# → [mcporter] Unable to parse function-style call.
# → Reason: Unsupported argument expression: AssignmentExpression.
```

mcporter only accepts:

- **Positional inside parens**: `mcporter call 'context7.resolve-library-id("react")'`
- **Single-string param inside parens with colon**: `mcporter 'context7.resolve-library-id(libraryName: "react")'`
- **Key=value flags after selector** (the easiest from a shell): `mcporter call exa.web_search_exa query="..." numResults=10`

Recommended pattern for agents:

```bash
mcporter call 'exa.web_search_exa' query="trending topics on X this week" numResults=10
```

Always wrap the selector in single quotes so the shell preserves it.

## 2. Twitter/X "what's trending" without a Twitter cookie

Agent Reach lists Twitter as a configurable channel — but **Cookie 还没配** is a
common state. When the user asks "X 上什么话题在火 / Twitter trends" you have
several no-auth paths:

**Path A — Exa semantic search (mcporter, already configured by Agent Reach)**

```bash
mcporter call 'exa.web_search_exa' \
  query="trending topics on X Twitter today viral June 2026" \
  numResults=10
```

Exa often returns trends24.in directly, with the actual trending list embedded
in the result highlights. This is the fastest path to "what's trending right
now globally / per region".

**Path B — Jina Reader against trends24.in (zero config, more reliable than Exa for raw lists)**

```bash
curl -sL "https://r.jina.ai/https://trends24.in/"                # Worldwide
curl -sL "https://r.jina.ai/https://trends24.in/united-states/"  # US
curl -sL "https://r.jina.ai/https://trends24.in/japan/"          # Japan
# ... see trends24.in/<country>/ for all geo slugs
```

Output is clean markdown — buckets of trending hashtags / phrases at 30-min
granularity over the last 24 hours. No auth, no rate limits worth worrying
about for occasional reads.

**Path C — Exa for AI/topic-niche discussion**

For "what are people on X saying about <topic>", Exa returns relevant tweet
threads and quote-replies (with view counts) collated from articles + thread
roll-ups. Better signal than trends24 when the user asks about a specific
discussion rather than the global trending list.

```bash
mcporter call 'exa.web_search_exa' \
  query="viral discussion on X Twitter about <topic> this week" \
  numResults=8
```

## Why this matters

Without these patterns, the agent will:
- Get stuck on the `mcporter call 'a.b(x=1)'` syntax error and either give up or
  fall back to crude `curl` of unauthenticated Twitter (which Twitter blocks).
- Tell the user "Twitter 渠道还没装 Cookie，没法看 trends" — incorrect, because
  trends24 + Exa give a high-quality answer with zero config.

The right framing for the user: "**Twitter 渠道还没装 Cookie，这里走 Web 路线 ——
能看公开热搜 + 被搜索引擎收录的爆贴，但拿不到 X 内部 API 的'For You / 分类趋势'
和实时互动数。**" Then deliver via Path A + B + C.
