# Intelligence Sources Directory

## Source 1: 今日热榜 (TopHub)

- **URL**: https://tophub.today
- **Tech section**: https://tophub.today/c/tech
- **Focus**: 全平台热榜聚合
- **Coverage**: 微博、知乎、抖音、GitHub Trending、Product Hunt、Hacker News、V2EX、掘金等
- **Access notes**: 
  - May trigger CAPTCHA ("安全验证") on automated access from non-Chinese IPs
  - If blocked, skip — aihot.today + buzzing.cc cover similar ground
- **Best for**: 广泛的社会热点 + 技术趋势

## Source 2: AI今日热榜 (AIHot)

- **URL**: https://aihot.today
- **Focus**: AI专线新闻聚合
- **Coverage**: 50+来源，包括 TechCrunch、36Kr、Hacker News、GitHub Trend、Product Hunt、HuggingFace、OpenAI Blog、Anthropic Blog 等
- **Update frequency**: 24/7 实时更新
- **Access notes**:
  - Fully accessible via browser, no CAPTCHA observed
  - Rich content — each source lists 15-20 headlines with subtitles
  - Has a "切换到原文" toggle for Chinese/English
  - **Richest source — start here**
- **Best for**: AI行业新闻、融资、产品发布、技术研究

## Source 3: SoPilot

- **URL**: https://sopilot.net/zh/hot-tweets
- **Focus**: X (Twitter) 爆款帖实时监测
- **Coverage**: AI领域和Web3领域的起爆帖（发布后2小时内高互动帖子）
- **Features**: 
  - 爆款帖时间窗口监测
  - AI生成评论功能
  - Discord/RSS通知
- **Access notes**: Accessible via browser. Content is more about X platform dynamics than news headlines.
- **Best for**: 社交媒体趋势、X平台舆论方向

## Source 4: Buzzing

- **URL**: https://buzzing.cc
- **Focus**: 国外社交媒体热门讨论中文汉化
- **Coverage**: Hacker News、Reddit、Ars Technica、Axios 等热门讨论的中文翻译
- **Sections**: HN热门、Reddit热门、国外新闻头条、编辑精选
- **Access notes**: 
  - Fully accessible, large page (2600+ elements)
  - Each item shows: Chinese title, original English title, source domain, HN points/Reddit upvotes, timestamp
  - Excellent for deduplication — same stories as TechURLs but with Chinese translation
- **Best for**: 给中文用户阅读的HN/Reddit热门

## Source 5: TechURLs

- **URL**: https://techurls.com
- **Focus**: 英文科技新闻多平台聚合
- **Coverage**: Hacker News、Reddit /r/technology、Wired、Ars Technica、The Verge、TechCrunch 等
- **Access notes**: 
  - Clean layout, headlines with timestamps
  - Reddit /r/technology section showed "1y" timestamps (possibly stale data)
  - HN section is fresh
- **Best for**: 英文科技头条速览

---

## Short Link Resolution

The original source list was shared via a tweet with t.co short links. Resolution method:

| Short link | Resolves to | Source |
|------------|-------------|--------|
| t.co/oXcTwmUjZz | tophub.today/c/tech | 今日热榜 |
| t.co/09fP3SSGNB | aihot.today | AI今日热榜 |
| t.co/5uylCfKnla | sopilot.net/zh/hot-tweets | SoPilot |
| t.co/ysze5bZ2uj | buzzing.cc | Buzzing |
| t.co/Jfqvf3vDfV | techurls.com | TechURLs |

**Resolution technique**: Navigate to each t.co link in the browser. The final URL appears in the `browser_navigate` response's `url` field. Do NOT use `curl -sI` — it may time out.

---

## Deduplication Strategy

The same story often appears across multiple sources:

| Story pattern | Appears on | Keep version from |
|---------------|------------|-------------------|
| HN top story | Buzzing + TechURLs | Buzzing (has Chinese translation) |
| TechCrunch AI article | aihot.today + TechURLs | aihot.today (has Chinese subtitle) |
| 36Kr article | aihot.today only | aihot.today |
| GitHub trending | tophub.today + aihot.today | Either (dedupe by repo name) |

## Recommended Scrape Order

1. **aihot.today** — richest source, covers TechCrunch/36Kr/HN/GitHub/PH
2. **buzzing.cc** — HN/Reddit Chinese translations, catches what aihot misses
3. **techurls.com** — English headlines for cross-reference
4. **tophub.today** — skip if CAPTCHA blocked (aihot covers similar ground)
5. **sopilot.net** — optional, for X platform trends specifically
