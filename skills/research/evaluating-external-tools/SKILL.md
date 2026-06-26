---
name: evaluating-external-tools
description: |
  USE WHEN the user shares a URL — GitHub repo, blog post, product page, tool
  release — and asks "研究一下", "看看有帮助吗", "有用吗", "评估一下", "what is X",
  "should I use Y", "is Z worth installing", or similar.

  Output is a fit-evaluation against the user's ACTUAL existing setup (their
  installed skills, configs, cron jobs, tools), with high-value use cases tied
  to their real workflow + explicit gaps/overlaps + 3-4 concrete next-step
  options.

  NOT a README translation. NOT a hello-world tutorial. NOT a generic feature
  tour.

  Triggers: 研究一下 / 看看 / 评估 / 有帮助吗 / 值得装吗 / 对我有用吗 / what is /
  should I / is X worth.
version: 1.0.0
tags: [research, evaluation, recommendation, decision-making]
---

# Evaluating External Tools

How to respond when the user shares a link to a repo / tool / blog post and
asks for an evaluation. This skill captures the user's strong preferences for
this class of work, learned across multiple sessions.

## What the user actually wants

When the user says **研究一下这个** with a link, they are NOT asking for:
- A README translation (they can read English)
- A hello-world tutorial (explicit feedback: *不想做这么简单的事*)
- A generic feature tour
- "Here's what the project says about itself"

They ARE asking:
1. **Does this fit MY setup and workflow?**
2. **What can it concretely do for my work or personal life?**
3. **What should I do right now — install / partial install / skip / try one thing?**

The evaluation is a *fit decision*, not a tutorial.

## Workflow

### 1. Fetch the source (don't browse if you don't need to)

For plain README / blog: `curl -sL <url>` or `web_extract`. Use `browser_navigate`
only for sites that need JS or aggressive bot defenses (most do not).

Always read enough to see:
- Author / org (Apple, ex-Google, anon, …) — signal for quality
- License (MIT/Apache = OK to integrate; GPL = noted; AGPL = read carefully)
- Active maintenance (last commit, release cadence)
- Feature list (the actual capabilities, not the marketing)

### 1b. Batch evaluation (list of N tools)

When the user shares a link to a *listicle* or "top 10 tools" article, the
workflow shifts from single-tool fit-decision to **incremental gap analysis**:

1. Extract the full list (browser_console JS extraction is often needed —
   these articles truncate in snapshot).
2. For EACH item, check if the user already has an equivalent skill/tool:
   - `skills_list` + `skill_view` for existing coverage
   - Mark each as: ✅ already have / ❌ not relevant / 🟡 worth considering /
     ⚠️ heavy overlap
3. Output a single comparison table — not 10 separate evaluations.
4. Recommend installing **only 2-3** items that provide genuine incremental
   value. Explicitly say why the rest are skipped (overlap / not relevant).

The user does NOT want 10 install commands. They want to know "which 2 of
these 10 are worth my time given what I already have."

### 1c. Blocked-URL extraction

Some domains are blocked by `web_extract` (e.g. `douyin.com` short links,
`x.com` status pages, some `segmentfault.com` articles). When this happens:

1. Use `web_search` with key phrases from the shared text to find the same
   content mirrored on other platforms (segmentfault, zhihu, YouTube, X, Reddit).
2. If the mirror is also blocked, use `browser_navigate` + `browser_console`
   with `document.querySelector('article')?.innerText` to extract full text
   client-side. Articles that truncate in the accessibility snapshot often
   extract cleanly via JS.
3. Never give up after one blocked URL — the content almost always exists
   in multiple places.

### 2. Compare against the user's actual setup

This is the differentiator. Before writing a verdict:

- `skills_list` — what does the user already have?
- `read_file ~/.hermes/config.yaml` — what's their model, providers, cron, etc?
- `cronjob action=list` — what's running?
- Read installed equivalents (e.g. if it's a research tool, check `agent-reach`)

If a tool overlaps 80% with existing skills, **say so explicitly**. The user does
not want to install 5 things that do the same job.

### 3. Output structure

Keep it compact. The user reads chat on Weixin — wall-of-text loses them.

A good response has roughly these blocks:

```
# 🔬 <Tool Name> 评估

## 这是什么
<2-3 lines: author + core idea + key facts (Star, license, language)>

## 📚 核心能力 / 结构
<Compact table of what it actually does>

## 🆚 跟你现状对比
| 你已有 | 这工具提供 | 重叠？ |
| ... | ... | 🟢/🟡/🔴 |

## 🎯 对你的**真正**价值（3-5 个高价值用例）
- 用例 1: 绑定到用户某个 cron / skill / 工作流
- 用例 2: ...
- (跳过 hello-world / 基础教程类用例)

## ⚠️ 限制 / 风险（如果有）

## 💡 行动选项
- 选项 A: 全装（适合 X 情况）
- 选项 B: 只挑 N 个增量 — 推荐 ⭐
- 选项 C: 看一眼不动
- 选项 D: 另一种角度

## ⚖️ 一句话结论
<verdict + reason>

需要我 <最可能的 next action>？
```

### 4. Ask, don't drone

End every evaluation with an action question. Don't write 5 more paragraphs of
caveats. The user will tell you what they want next.

## Style rules (hard learned)

| Don't | Do |
|-------|-----|
| Start with "Hello world" demo | Jump straight to a use case tied to user's existing cron / skill / data |
| Translate the README | Quote 1-2 lines of distinguishing claims, rest is your analysis |
| List 20 features generically | List 3-5 capabilities the user will actually use |
| "X 是一个强大的 ... 工具" filler | "作者 Y（前 Google Chrome lead），24 个 skill 覆盖 6 个生命周期阶段" — concrete |
| Assume install | Compare to user's existing skills FIRST, then recommend install/partial/skip |
| Walls of text | Tables + bold verdicts + short bullets |
| Markdown-only English doc translation | Mix Chinese (user's language) with English technical terms preserved |

## Anti-patterns and rationalizations

| Excuse you'll be tempted by | What to do instead |
|-----------------------------|---------------------|
| "Better cover all features for completeness" | Cover ONLY features that matter for this user. Completeness is the README's job, not yours. |
| "I should explain the basics first" | The user shared the link — they've already glanced at the basics. Skip to fit. |
| "I'll start with a hello world to show it works" | This was explicitly rejected. Start with the highest-value use that fits THIS user's setup. |
| "Let me be neutral and just present info" | The user is asking for a recommendation. A non-recommendation IS a recommendation. State your verdict. |
| "I'll be safe and recommend installing everything" | This produces skill bloat / redundancy. Compare to existing first. Most cases the right answer is "装 2 个增量" not "装全套". |

## Verification before sending

Before pressing send, check:
- [ ] I read the actual README / page, not just the title
- [ ] I compared against at least one existing thing the user has installed
- [ ] My recommendation is concrete (装/不装/装哪几个)
- [ ] I ended with action options, not more analysis
- [ ] No hello-world demos in the use-cases section
- [ ] Total length fits a chat — if it's >4 screens, cut

## Examples from past sessions

These patterns scored well with the user across this class of task:

**Apple container** (well-received): led with "你是精准目标用户" + 你的环境刚好满足
matrix → then high-value uses tied to Hermes/maigret/cron workflow → ended with
3 action options.

**Cloudflare temp accounts** (initial response criticized): led with hello-world
deploy demo → user said *不想做这么简单的事*. Pivoted to 5 high-value uses
(webhook receiver, B 端 demo claim, LLM proxy, draft env for cron, agent-native
SaaS pattern). User happy.

**superpowers-zh** (well-received): immediately surfaced "你已经有 95% — 这是你
缺的 2 个" — saved user from installing redundant 20 skills.

**addy/agent-skills** (well-received): identified 4 unique skills the user
didn't have (doubt-driven, source-driven, observability, security-and-hardening)
and built install command around just those.

**Codex top-10 skills listicle** (well-received): user shared a douyin link →
web_extract blocked → web_search found segmentfault mirror → browser extracted
full article via JS. Output was a single 10-row table with "你已有？/ 有用吗 /
说明" columns, then recommended only 2 of 10 for install (mcp-builder +
academic-research), with explicit "已有等效替代" notes for the rest.

The common thread: **the response is shaped by what the user already has**, not
by what the tool offers.

## Related skills

- `agent-reach` — when the URL is a content source (article / video / forum
  thread), prefer routing through agent-reach's channels for the actual fetch.
- `hermes-agent` — for evaluating Hermes-ecosystem tools, cross-reference
  this skill's docs as authoritative.
- `prism-discover` / `prism-scan` — heavier structural analysis if the user
  asks for a deep teardown rather than a fit decision.
