---
name: stock-market-briefing
description: "Generate and deliver concise stock market briefings for A-shares, US stocks, ETFs, and user watchlists. Handles configured analysis projects when available and lightweight fallback reports when model/notification channels are missing."
version: 1.0.0
author: Hermes Agent
platforms: [macos, linux]
metadata:
  hermes:
    tags: [stocks, market-briefing, finance, feishu, watchlist]
---

# Stock Market Briefing

Use this skill when the user asks for stock analysis, a daily market note, A股/美股简报, watchlist review, or to send stock analysis to Feishu/WeChat.

## Core principles

- **Data integrity beats styling.** The user is strict about accuracy; verify actual fetched data before reporting.
- **Do the check before reporting.** Generate the artifact, inspect/validate it, then send the final brief.
- **Prefer Chinese output** for this user unless they ask otherwise.
- **Separate analysis from delivery.** If a project’s built-in notification channel is not configured, generate the report and deliver through the current Hermes channel rather than claiming the project pushed it.
- **Label limitations clearly.** If using a lightweight technical brief instead of a full LLM/news/fundamental report, say so.

## Workflow

1. **Identify the stock universe**
   - If the user gives codes, use those.
   - Otherwise use the existing configured watchlist when available.
   - For the user’s local daily stock project, the common watchlist includes US names like `NVDA, TSM, AAPL, ASML, GOOGL` and A股/ETF names like `600519, 300750, 601398, 510050, 510300, 159915, 513100`; re-check current config before relying on this.

2. **Check the existing project first when relevant**
   - Local project commonly lives at `/Users/jushuai/My_Project/daily_stock_analysis`.
   - Entry points usually include:
     - `python main.py --stocks <codes>`
     - `python main.py --market-review`
     - `python main.py --check-notify`
   - If the project has working model and notification config, use its normal report pipeline.

3. **If built-in model/notification config is missing, use a lightweight fallback**
   - Fetch public price/history data directly with available finance libraries/APIs.
   - Compute simple indicators: daily pct change, MA5, MA20, RSI.
   - Classify each symbol as `偏强/持有`, `震荡/观察`, or `偏弱/谨慎` from transparent rules.
   - Deliver through the active chat/Feishu session as Markdown.

4. **Validate before delivery**
   - Run the report generator and inspect the first 100–200 lines or saved Markdown.
   - Confirm at least one US stock and one A股/ETF row populated if the user asked for both.
   - If some tickers fail, include an `数据异常` section instead of hiding failures.

5. **Delivery format**

```markdown
# 📈 今日股票分析｜美股 + A股

生成时间：YYYY-MM-DD HH:mm（北京时间）
数据源：...；结论为技术面速览，不构成投资建议。

## 🌍 主要指数
- ...

## 🇺🇸 美股自选
| 标的 | 收盘 | 涨跌 | MA5 | MA20 | RSI | 结论 |
|---|---:|---:|---:|---:|---:|---|

## 🇨🇳 A股/ETF自选
| 标的 | 收盘 | 涨跌 | MA5 | MA20 | RSI | 结论 |
|---|---:|---:|---:|---:|---:|---|

## 📌 今日操作提示
- ...
```

## Pitfalls

- Do not say “已通过项目推送到飞书” unless the project’s notification diagnostic confirms a Feishu/Webhook/App Bot channel is configured and the send path actually returned success.
- If `.env` has only partial Feishu app credentials or no webhook/chat ID, it is not enough for static project notifications. Use Hermes delivery or ask for the missing config.
- A-share data sources may disagree or fail through stale proxy variables; a robust fallback is to try Yahoo Finance suffixes (`.SS`, `.SZ`) before or alongside AkShare.
- Do not over-interpret a technical-only report as full investment advice. Clearly mark it as a technical snapshot when news/fundamentals/LLM analysis were not used.

## References

- See `references/lightweight-technical-brief.md` for a compact fallback design and indicator rules.
