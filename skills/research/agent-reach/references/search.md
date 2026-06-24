# 搜索工具

Exa AI 搜索引擎。

## Exa AI 搜索

高质量 AI 搜索引擎，擅长技术和代码搜索。

```bash
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'
mcporter call 'exa.get_code_context_exa(query: "code question", tokensNum: 3000)'
```

### 使用场景

| 场景 | 参数 |
|-----|------|
| 网页搜索 | `web_search_exa(query: "...", numResults: 5)` |
| 代码搜索 | `get_code_context_exa(query: "...", tokensNum: 3000)` |

### ⚠️ mcporter call 语法陷阱

mcporter 接受**两种**调用形式，**别混用**：

| ✅ 正确 | ❌ 错误 |
|---|---|
| `mcporter call 'exa.web_search_exa(query: "q", numResults: 5)'` | `mcporter call 'exa.web_search_exa(query="q", numResults=5)'` |
| `mcporter call 'exa.web_search_exa' query="q" numResults=5` | `mcporter call exa.web_search_exa(query="q")` (没引号) |

- **括号内必须用 `:`**（TypeScript object literal 风格），用 `=` 报 `Unsupported argument expression: AssignmentExpression`
- **flag 形式没括号、用 `=`**：`mcporter call 'server.tool' k1=v1 k2=v2`
- **整个 expression 必须用单引号包起来**，否则 shell 会吞掉括号和逗号

调用前先看 schema，schema 里没列出的参数静默失败（例：Exa 的 `web_search_exa` 只接受 `query` 和 `numResults`，传 `includeDomains` 会被忽略）：

```bash
mcporter list exa --schema    # 看每个 tool 的参数
```

如果某个搜索想限定到 x.com / reddit.com 这类站点，**把限定写进 query 里**（"site:x.com viral discussion"），不要传一个 schema 不支持的字段。

### 特点

- 擅长英文内容和技术文档
- 支持代码上下文搜索
- 结果质量高

## 与其他搜索工具对比

| 工具 | 来源 | 适用场景 |
|-----|------|---------|
| Exa | agent-reach | 英文/技术/代码搜索 |
| 智谱搜索 | my-mcp-tools | 中文搜索 |
| GitHub 搜索 | agent-reach (dev.md) | 仓库/代码搜索 |
