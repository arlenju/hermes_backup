---
name: daily-news-briefing
description: "Compile a daily AI/tech news briefing from multiple aggregator sources. Scrape headlines, categorize by theme, format for push delivery."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos]
metadata:
  hermes:
    tags: [news, daily-briefing, ai-news, tech-news, aggregator]
---

# Daily News Briefing

Compile a categorized daily news briefing from multiple intelligence aggregator sources. Designed for push delivery via chat (WeChat/Feishu/Telegram).

## When to Use

- User asks for a daily news digest, AI/tech briefing, or "今日新闻"
- User shares a source list (tweet, blog post) and wants recurring news compilation
- Setting up a cron job for daily news push

## Intelligence Sources

See `references/sources.md` for the full source directory with URLs, characteristics, and scraping notes.

Current source set (5 sources):

| # | Source | URL | Focus |
|---|--------|-----|-------|
| 1 | 今日热榜 | tophub.today | 全平台热榜聚合（微博/知乎/抖音/GitHub/PH/HN） |
| 2 | AI今日热榜 | aihot.today | AI专线，50+来源，实时更新 |
| 3 | SoPilot | sopilot.net | X平台爆款帖实时监测 |
| 4 | Buzzing | buzzing.cc | Reddit/HN热门中文汉化 |
| 5 | TechURLs | techurls.com | 英文科技多平台聚合 |

## Workflow

1. **Scrape each source** using browser_navigate + browser_snapshot (full=true). These are dynamic JS sites — web_extract won't work.
2. **Resolve short links** (t.co etc.) by navigating to them in the browser — the redirect URL appears in the response.
3. **Dedupe across sources** — the same story often appears on HN, Buzzing, and TechURLs simultaneously. Keep the version with the most context.
4. **Categorize** into themes. Good default categories:
   - 🤖 AI大事件 (model releases, lab moves, major announcements)
   - 💰 AI商业与资本 (funding, valuations, business models)
   - 🔬 技术与学术 (papers, tools, benchmarks, research breakthroughs)
   - 🌐 国际科技 (policy, infrastructure, non-AI tech)
   - 📱 社会与趋势 (industry shifts, societal impact)
5. **Format for chat**: compact, numbered lists, emoji category headers. Keep each item to one line. Include source attribution line at top.
6. **Push** directly in the response. For daily automation, set up a cron job.

## Output Format

```
📰 每日AI科技简报 | {date}

情报源：{source1} · {source2} · ...

---

🤖 AI大事件
  1. {headline}
  2. {headline}
  ...

💰 AI商业与资本
  1. ...

🔬 技术与学术
  1. ...

🌐 国际科技
  1. ...

📱 社会与趋势
  1. ...

---

📌 信息源说明
  1️⃣ {source} {url} — {one-line description}
  ...
```

## Setting Up Daily Automation

Use cronjob to schedule daily push. Example:

```
schedule: "0 8 * * *"  # 每天早上8点
prompt: "抓取今日AI科技新闻并推送简报。情报源见 references/sources.md。"
skills: ["daily-news-briefing"]
```

Key points for cron setup:
- The cron runs in a fresh session with no chat context — the prompt must be self-contained.
- Load this skill so the agent knows the sources and format.
- Deliver to the user's preferred channel (WeChat/Feishu).

## Pitfalls

- **tophub.today may trigger CAPTCHA** on automated access. If blocked, skip it and rely on aihot.today + buzzing.cc which cover similar ground.
- **aihot.today has the richest content** — start there, then supplement with the others.
- **Don't use web_extract for these sites** — they're JS-rendered. Use browser tools.
- **t.co links need browser resolution** — curl -sI may time out. Navigate in browser to get the redirect URL.
- **Deduplication is critical** — HN top stories appear on both buzzing.cc and techurls.com. Pick the Chinese-translated version from Buzzing for Chinese-speaking users.

## Source Discovery

If the user shares a new source list (e.g., a tweet listing aggregator sites):
1. Extract all URLs from the content.
2. Resolve each short link to its destination.
3. Evaluate: does it cover a unique niche? Is it accessible?
4. Add promising sources to `references/sources.md`.
5. Test by scraping a sample before adding to the daily rotation.
