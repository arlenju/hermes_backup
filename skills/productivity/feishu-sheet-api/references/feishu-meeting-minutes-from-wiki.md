# Feishu Wiki + Uploaded DOCX → Internal Meeting Minutes

## Trigger
Use when the user provides an uploaded meeting-minutes DOCX plus a Feishu Wiki/Doc URL and asks to fill or rewrite specific sections, especially with “不要有 AI 味”.

## Workflow
1. Read the uploaded DOCX first to preserve the original header fields: title, meeting time, meeting place, attendees, subject, attachment section, and numbering style.
2. Check for template residue or topic mismatch. If the title is about one topic but the body contains unrelated copied content, replace the unrelated body rather than polishing it.
3. Resolve the Feishu Wiki URL:
   - `GET /wiki/v2/spaces/get_node?token=<wiki_node_token>`
   - Use `data.node.obj_token` and `data.node.obj_type`.
   - For `obj_type == "docx"`, read `GET /docx/v1/documents/{obj_token}/raw_content`.
4. Extract only the facts needed for the minutes: background, issues found,整改/调整方向, review conclusion, follow-up actions, and attachments.
5. Draft only the requested sections unless the user asks for the full document. Preserve the document’s numbering (`1、…`, `2、…`, `3、附件`) and internal memo tone.
6. If the user gives a review conclusion such as “宋总评审通过”, write it plainly in the decision paragraph: “经会议讨论，宋总对本次…方案进行了评审，并同意通过。”

## Style: “不要有 AI 味”
- Keep it concise and businesslike; do not over-explain.
- Use natural internal wording: “本次会议主要围绕…进行评审”, “会议对…进行了讨论”, “后续…按照…执行”.
- Avoid inflated transitions and slogans: “综上所述”, “显著提升”, “全方位赋能”, “闭环管理” unless they are in the source.
- Do not invent detailed decisions or timelines that are not in the source. If needed, phrase as follow-up responsibilities rather than fabricated commitments.
- For meeting minutes, prefer concrete action bullets over generic “加强管理/持续优化”.

## Output pattern
```markdown
## 1、会议议程及主要内容
本次会议主要围绕……进行评审。

根据……，本次检查发现……。为进一步……，……对……进行了梳理和调整，并提交本次评审。

会议重点讨论以下事项：
1. ……
2. ……
3. ……

经会议讨论，……评审通过。本次调整可作为后续……的依据。

## 2、后续跟进事项
1. 请……根据本次评审意见，更新……。
2. 请……完成系统/流程中的相关调整。
3. 后续申请中，需严格按照更新后的范围执行。
4. 执行过程中如发现……，应及时反馈并调整。
```

## Pitfalls
- Do not leave unrelated template residue in the rewritten sections.
- Do not turn a short internal meeting minute into a policy essay.
- Raw content may omit rich tables/images; for attachment tables, mention the attachment by name rather than reconstructing rows unless the user supplies the table content.
