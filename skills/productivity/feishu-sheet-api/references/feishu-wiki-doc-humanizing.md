# Feishu Wiki/Docx Reading and Humanizing Notes

## Trigger
Use this when the user shares a Feishu Wiki URL and asks to summarize, polish, rewrite, or remove AI tone.

## Workflow
1. Extract the Wiki node token from `/wiki/<token>`.
2. Resolve the node:
   - `GET https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token=<node_token>`
   - Read `data.node.obj_token`, `data.node.obj_type`, and `data.node.title`.
3. If `obj_type == "docx"`, read raw text:
   - `GET https://open.feishu.cn/open-apis/docx/v1/documents/{obj_token}/raw_content`
4. Use raw content for fast summarization/润色.
5. If content ends before expected table/image/colored sections, tell the user raw_content likely omitted rich blocks and offer to read block structure or export to docx/pdf.

## Markdown export caveat
Some Feishu tenants reject Drive export with `file_extension=md`:

```json
{"code":99992402,"field":"file_extension","description":"file_extension is optional, options: [docx,pdf,xlsx,csv,base,pptx]"}
```

Do not treat this as a blocker for text work. Fall back to `docx/v1/documents/{token}/raw_content`.

## Humanizing style for internal compliance /整改文档
When the user says “不要有 AI 味”:
- Preserve the original structure and facts; do not over-expand.
- Prefer direct business language: “根据…要求”, “本次检查发现…”, “为进一步规范…”.
- Avoid AI-sounding transitions: “综上所述”, “首先/其次/最后” when not needed, “显著提升”, “赋能”, “全方位”.
- Split ambiguous paragraphs into clear headings: 背景、问题、整改计划、整改步骤、调整说明.
- Keep tone formal but human; avoid excessive adjectives and policy-slogan phrasing.
