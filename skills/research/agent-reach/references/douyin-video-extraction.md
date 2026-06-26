# 抖音（Douyin）视频内容提取

## 适用场景

用户分享抖音短链接（`https://v.douyin.com/xxxxx`），要求研究/分析/写报告。
抖音无 API，web_extract 被 IP 限制屏蔽，需要用浏览器 + JS 提取。

## 提取流程

### 1. 浏览器打开短链接

```python
browser_navigate(url="https://v.douyin.com/El9ZrPC4GAM/")
```

短链接会 302 重定向到完整 URL：`https://www.douyin.com/video/7641427358809991528`

### 2. 等待视频加载

页面初始显示"视频数据加载中"，需要 scroll 一下或等待几秒。

### 3. 用 JS 提取页面完整内容（关键步骤）

抖音的 DOM 不会在 accessibility tree 中暴露视频描述、章节摘要、评论等信息。必须用 `browser_console` 执行 JS：

```javascript
// 获取页面标题
document.title
// → "全哥在抖音记录美好生活20260519 - 抖音"

// 获取所有文本内容（包含 AI 生成的章节摘要、评论、作者信息）
JSON.stringify({
  title: document.title,
  meta: document.querySelector('meta[name="description"]')?.content,
  og_title: document.querySelector('meta[property="og:title"]')?.content,
  og_desc: document.querySelector('meta[property="og:description"]')?.content,
  h1: document.querySelector('h1')?.textContent,
  url: window.location.href,
  all_text: document.body.innerText
})
```

### 4. 从提取的文本中识别关键信息

抖音页面文本通常包含：
- **AI 章节摘要**：标有"章节要点"和"内容由AI生成"，包含视频各章节的时间戳和要点
- **视频描述**：作者写的文案
- **互动数据**：点赞数、评论数、分享数、收藏数
- **评论区**：热门评论及回复
- **作者信息**：用户名、粉丝数、获赞数
- **搜索建议**：页面底部的相关搜索词

### 5. ASR 语音转写（如果需要视频口述内容）

抖音网页版视频有声音但无法直接转录。如果用户需要视频里说的原话：
- 无法从网页直接提取音频流
- 需要用户在手机上录屏/录音后发送音频文件
- 收到音频后用 STT 管道转写（见 voice-pipeline skill）

## 实际案例

用户分享 `https://v.douyin.com/El9ZrPC4GAM/`，要求研究并写报告：

1. 浏览器打开 → 重定向到 `douyin.com/video/7641427358809991528`
2. JS 提取到：
   - 作者：全哥（55.2万粉丝，302万获赞）
   - 发布时间：2026-05-19 10:40
   - 视频时长：09:36
   - AI 章节摘要：
     - 00:00 美股存储暴跌
     - 01:56 底层人的劣根性
     - 05:49 远离底层人
     - 09:05 结语
   - 热门评论：讨论做空存储、白银、特斯拉等
3. 根据 AI 摘要 + 评论内容，结合 web_search 补充背景信息，生成研究报告

## 注意事项

- 抖音网页版需要登录才能看到部分内容，但未登录状态下 AI 章节摘要和基本信息仍可见
- `web_extract` 和 `web_search` 对抖音域名均返回"Blocked: private/internal network"，必须用浏览器
- 页面底部有大量相关视频链接，可帮助发现相关内容
- 搜索框中的预填词（如"美光科技"）是抖音根据视频内容自动提取的关键词，可作为研究线索
