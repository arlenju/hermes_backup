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
When the user says "不要有 AI 呫":
- Preserve the original structure and facts; do not over-expand.
- Prefer direct business language: "根据…要求", "本次检查发现…", "为进一步规范…".
- Avoid AI-sounding transitions: "综上所述", "首先/其次/最后" when not needed, "显著提升", "赋能", "全方位".
- Split ambiguous paragraphs into clear headings: 背景、问题、整改计划、整改步骤、调整说明.
- Keep tone formal but human; avoid excessive adjectives and policy-slogan phrasing.

## Meeting minutes humanizing (会议纪要)
Meeting minutes have their own conventions distinct from compliance docs:
- Use "一是/二是/三是/四是" for numbered points within a paragraph, not bullet lists or "1. 2. 3." — this reads like meeting notes typed by a person, not AI-generated.
- Write decisions in passive voice: "经会议讨论，宋总对本次方案进行了评审，并同意通过" — not "经过深入讨论后评审通过".
- Keep paragraphs as dense blocks, not one-sentence-per-line. Real meeting minutes pack related points together.
- For follow-up items (后续跟进事项), use imperative sentences without subject: "请网络团队根据本次评审意见，更新…" — not "网络团队应该更新…".
- End with "（全文结束）" as a document terminator, matching internal template style.

## DOCX editing workflow (supplement existing document from Wiki content)
When the user sends an existing DOCX (e.g., meeting minutes template) and a Feishu Wiki URL, asking to supplement/rewrite specific sections:

1. Read the existing DOCX with `python-docx` to understand structure (paragraphs + tables).
2. Read the Wiki raw_content (workflow above) for the source material.
3. Replace/add paragraphs in-place using `python-docx`:
   - `doc.paragraphs[i].text = new_text` to replace content of an existing paragraph.
   - `doc.add_paragraph(text)` to append new paragraphs.
   - Preserve the header table (备忘录/OFFICE MEMORANDUM template) — do not touch `doc.tables`.
4. Save to Desktop with `_修订版` suffix.
5. Deliver via `MEDIA:/path/to/file.docx`.

**Key points:**
- Install python-docx first: `~/.hermes/hermes-agent/venv/bin/python -m pip install python-docx` (or `uv pip install python-docx` if pip is missing).
- Read existing DOCX structure first: `doc.paragraphs` (list), `doc.tables` (list). Print them to understand the template before editing.
- Do NOT recreate the document from scratch — edit in-place to preserve formatting, tables, headers.
- Self-verify after save: re-open the saved DOCX, print paragraphs and tables to confirm content replaced correctly.

## Creating new DOCX documents from scratch (research reports, etc.)

When there is no existing template to edit (e.g., user asks for a research report as a Word doc):

1. Write the full report content as Markdown first (`write_file` to `/tmp/report.md`). This lets you review structure before converting.
2. Convert to DOCX with `python-docx`:
   - `doc = Document()` — start fresh
   - `doc.add_heading(text, level=1)` for `#` headings, level=2 for `##`, etc.
   - `doc.add_paragraph(text)` for body text
   - `doc.add_table(rows, cols)` for structured data; set `table.style = 'Table Grid'` for borders
   - `doc.save('/path/to/output.docx')`
3. Save to Desktop with descriptive filename.
4. Deliver via `MEDIA:/path/to/file.docx`.
5. Self-verify: re-open saved DOCX, print paragraph count and table count to confirm.

**Key points:**
- `Table Grid` style gives visible borders; without it tables are borderless.
- `add_heading` automatically applies Word's built-in Heading 1/2/3 styles — no manual formatting needed.
- For bold inline text within a paragraph, use `run = doc.add_paragraph().add_run('text')` then `run.bold = True`.
- Install python-docx into Hermes venv: `uv pip install --python ~/.hermes/hermes-agent/venv/bin/python python-docx`.
