# Twitter/X 热搜与热门话题（无 Cookie 路径）

适用场景：用户问「X 上最近什么火」「Twitter 这两天热搜是什么」「推特上大家在讨论什么」，**且 Twitter Cookie 还没配**（`agent-reach doctor` 显示 twitter 渠道未激活）。

不要让用户先去配 Cookie 再回来 —— 这条链路用零配置渠道就能给出像样的答复。Cookie 路线只在用户明确要看「某关键词最近 N 小时的高互动 thread 全文」时才需要。

## 路线图

| 想要什么 | 用什么 | 命令 |
|---------|--------|------|
| 实时热搜榜（按区域） | trends24.in via Jina Reader | `curl -s "https://r.jina.ai/https://trends24.in/<region>"` |
| 中文/AI/科技圈正在讨论的话题 | Exa 跨站语义搜索 | `mcporter call 'exa.web_search_exa(query: "viral discussion on X about <topic> June 2026", numResults: 8)'` |
| 单条爆款贴子的全文 | Exa 限定域名 + Jina Reader 兜底 | query 里写 "site:x.com OR site:twitter.com" |

## 1. trends24.in：拿区域实时热搜榜

trends24 是 trends24.in 的镜像聚合服务，公开页面、不需要 Cookie，包含全球+各国 Twitter trends。直接用 Jina Reader 把页面读成 markdown：

```bash
# 全球
curl -s "https://r.jina.ai/https://trends24.in/"

# 美国
curl -s "https://r.jina.ai/https://trends24.in/united-states/"

# 日本 / 中国大陆 / 台湾 / 香港
curl -s "https://r.jina.ai/https://trends24.in/japan/"
curl -s "https://r.jina.ai/https://trends24.in/china/"
curl -s "https://r.jina.ai/https://trends24.in/taiwan/"
curl -s "https://r.jina.ai/https://trends24.in/hong-kong/"
```

输出结构：「Top 50, last 24h」按时间切片（每条 trend 上次出现时间），抓回来直接能用。

> 实测 2026-06：全球榜会被印度+日本市场刷屏（这两个市场时区+发推密度最高）。要看美国/中国/欧洲讨论，**直接调对应区域 URL**，别只看全球榜。

## 2. Exa：拿"AI/科技/特定话题在 X 上的高互动讨论"

trends24 给关键词，但不告诉你**为什么**它在火。Exa 能直接索引到 X 上的爆贴、被新闻站点 quote 的推文，以及对推文的二次解读：

```bash
# AI 圈瓜
mcporter call 'exa.web_search_exa(query: "viral discussion on X Twitter AI LLM this week June 2026", numResults: 8)'

# 某个具体关键词
mcporter call 'exa.web_search_exa(query: "X Twitter posts about <keyword> high engagement", numResults: 10)'

# 限定到 x.com（写进 query，不要用不支持的 includeDomains 字段）
mcporter call 'exa.web_search_exa(query: "site:x.com OR site:twitter.com <keyword> trending", numResults: 8)'
```

Exa 返回每条结果会带：URL、标题、发布时间、关键 highlight 片段（含原推文里的引用文本和浏览/赞数据）。把多条 highlight 拼起来就够写一段 X 圈瓜总结。

## 3. 推荐的混合工作流

「最近 X 上什么话题火」类问题，按这个序列跑：

1. **trends24 全球榜** —— 知道宏观什么在刷屏
2. **trends24 区域榜（按用户语境选 1-2 个）** —— 中文用户大多想知道中国大陆/美国/日本，不是印度
3. **Exa 跨站搜索 1-2 个聚焦查询** —— 拿到有具体内容的 thread / 报道，区分"出现频率高"和"讨论质量高"
4. **汇报时分板块**：全球热搜 / 区域热搜 / AI 或用户关心的细分领域

不要把 trends24 的整个 Top 50 表全部贴给用户，**按板块归类**（金融/政治/娱乐/体育/AI），并把语种相关性弱的（如印地语、土耳其语 hashtag）合并成一行。

## 什么时候才升级到 Twitter Cookie

只有这些情况值得让用户配 Cookie：

- 要看**某账号的时间线**（`twitter user-posts @user`）
- 要拿**特定推文的回复树**（`twitter tweet URL`）
- 要做**Twitter 内部 search**（关键词 → 推文，trends24 + Exa 给不出的 niche 话题）
- 用户说「我想看大家 quote 了什么」「这条推文下面的争论是啥」

否则 trends24 + Exa 已经够用，不要绕弯让用户去导 Cookie。
