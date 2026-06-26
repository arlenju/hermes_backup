---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf). Generate PDFs from HTML/Markdown via Chrome headless. Generate DOCX via python-docx."
version: 2.5.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Fast Image OCR: PP-OCRv6 helper (recommended for screenshots)

For screenshots, fund/stock app images, chat screenshots, and other image-only OCR, use the local PP-OCRv6 helper when available:

```bash
~/.hermes/scripts/ocr_image.sh /path/to/image.jpg          # plain text
~/.hermes/scripts/ocr_image.sh /path/to/image.jpg --json   # text + boxes + scores
```

Installed pattern (proven on macOS M5):

```bash
BASE="$HOME/.hermes/ocr_ppocrv6"
python3 -m venv "$BASE/venv"
source "$BASE/venv/bin/activate"
pip install -U pip setuptools wheel
pip install 'paddleocr>=3.7.0' paddlepaddle
```

Implementation files:
- `~/.hermes/ocr_ppocrv6/ocr_image.py` — Python wrapper around PaddleOCR 3.x / PP-OCRv6
- `~/.hermes/scripts/ocr_image.sh` — Hermes-facing shell entrypoint
- models cache in `~/.paddlex/official_models/` (first run downloads PP-OCRv6_medium_det/rec and orientation model)

Performance note: first run includes model downloads (~47s observed). Warm run with medium model through Python wrapper was ~6s on a chat screenshot. For sub-100ms browser-style OCR, use Tiny + ONNX/WebGPU/daemon mode; the Python helper prioritizes accuracy and simple Hermes integration.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

## PDF Generation (HTML/Markdown → PDF)

When the user asks to "转成PDF" / "convert to PDF" / "export as PDF", the most reliable path on macOS is **Chrome headless**.

### ✅ Chrome Headless (recommended — handles CJK perfectly)

```bash
# 1. Write content as HTML to a temp file (see markdown→HTML conversion below)
# 2. Use Chrome to render HTML → PDF
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless \
  --disable-gpu \
  --no-sandbox \
  --print-to-pdf="/path/to/output.pdf" \
  --print-to-pdf-no-header \
  "/tmp/input.html"
```

**Why this works:** Chrome's rendering engine handles CJK fonts, tables, CSS styling, and multi-page layout natively. Output quality is identical to Chrome's "Print to PDF" in the browser. No Python dependencies needed.

**CSS tip:** Use `@page { margin: 2cm; }` in the HTML `<style>` to control page margins. PingFang SC / Heiti SC are available system fonts for Chinese.

### Markdown → HTML → PDF conversion

For generating a PDF from Markdown content, first convert MD to styled HTML with Python, then use Chrome headless:

```python
import html
# Simple MD→HTML: handle # headings, | tables |, - lists, **bold**, `code`, ---
# Write to /tmp/report.html with a <style> block for fonts/margins/tables
# Then call Chrome headless on the HTML file
```

A working pattern: write a Python script to `/tmp/md_to_pdf.py` that reads the `.md` file, converts to HTML with basic styling (font-family: "PingFang SC", table borders, h1/h2/h3), saves HTML, then `subprocess.run` Chrome headless.

### ❌ Methods that DON'T work well (pitfalls)

| Method | Problem |
|--------|---------|
| `cupsfilter -i text/html -m application/pdf` | Returns "无滤镜可从text/html转换成application/pdf" — no HTML filter on macOS |
| `textutil` | Only converts between txt/html/rtf/doc — cannot output PDF |
| `fpdf2` (Python) | `FPDFException: Not enough horizontal space to render a single character` with CJK text, even with TTF font registration. Table rendering also fails. |
| `docx2pdf` (Python) | Requires Microsoft Word installed; not available on this machine |
| `reportlab` | Heavy dependency, CJK font registration is complex |

### DOCX Generation (python-docx)

For generating Word documents (when user wants .docx not .pdf):

```bash
# Install into system Python (not venv — python-docx is pure Python, no conflicts)
uv pip install --system python-docx
```

**Reusable script:** `scripts/md_to_docx.py` — a proven Markdown→DOCX converter that handles headings, tables (with bold header row + Table Grid style), bullet/numbered lists, code blocks (Courier New 9pt), `**bold**` inline formatting, and `---` horizontal rules. Used across multiple sessions for generating research reports as Word documents.

```bash
python3 scripts/md_to_docx.py /tmp/report.md /Users/jushuai/Desktop/report.docx
```

The script auto-verifies output by reopening the docx and printing paragraph/table counts.

**Manual pattern** (if you need custom formatting beyond the script):

```python
from docx import Document
from docx.shared import Pt, Cm
doc = Document()
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
doc.add_heading('Title', 0)
doc.add_paragraph('Content...')
# Tables: table = doc.add_table(rows=N, cols=M); table.style = 'Table Grid'
# Bold header: for run in cell.paragraphs[0].runs: run.bold = True
doc.save('/path/to/output.docx')
```

**Pitfall:** `python-docx` is NOT in the Hermes venv by default. Install to system Python: `uv pip install --system python-docx`. Do NOT try `pip install` — pip may not exist as a standalone command.

### MD → DOCX reusable script

A proven conversion script is at `scripts/md_to_docx.py`. It handles:
- H1–H4 headings, bold (`**text**`), inline code
- Markdown tables (with bold header row, Table Grid style, 10pt font)
- Bulleted lists, nested bullets, numbered lists
- Code blocks (Courier New 9pt, indented)
- Horizontal rules, page margins (2.5cm)

```bash
# Usage: write report to /tmp/report.md, then:
python3 scripts/md_to_docx.py /tmp/report.md /Users/jushuai/Desktop/Report.docx
```

This script was proven across 3+ sessions generating research reports, meeting minutes, and technical documents. It avoids the common pitfalls of fpdf2 (CJK rendering failures) and cupsfilter (no HTML filter on macOS).

### DOCX → PDF (when user already has a .docx)

If the user has a DOCX and wants PDF, and Chrome is available:
1. Use `python-docx` to read the DOCX content
2. Convert to styled HTML
3. Use Chrome headless to render HTML → PDF

This is more reliable than trying to find a direct DOCX→PDF converter on macOS without LibreOffice or Word installed.

### Douyin (抖音) video content extraction

When a user shares a `v.douyin.com` short link and asks to research/analyze the content, use the browser + JavaScript console technique documented in `references/douyin-video-extraction.md`. This reliably extracts video titles, chapter summaries, author info, and comments without needing to play the video.

### X/Twitter post extraction

The same browser + console technique works for X/Twitter posts (`x.com/i/status/<id>`). Navigate to the URL, then use `browser_console` to extract `document.body.innerText` — the full post text, engagement counts, and embedded links are all in the text. See `references/douyin-video-extraction.md` for the X/Twitter variant.

### Research report generation from video/social media content

When a user shares a Douyin/X link and asks for a research report ("研究一下", "做个报告"), the proven end-to-end workflow is: extract content → web_search for background → synthesize into structured Markdown report → convert to DOCX via `scripts/md_to_docx.py` or PDF via Chrome headless → deliver via `MEDIA:`. This was proven across 4+ reports in a single session.

---

## CHM → PDF Conversion

CHM (Compiled HTML Help) files are common for Chinese vendor documentation (Huawei, etc.). They are essentially LZX-compressed CAB containers with HTML pages, images, and an HHC table-of-contents file.

### Tools needed

```bash
brew install sevenzip    # 7zz — extracts CHM contents (chmlib only gets internal structure files)
pip install pypdf        # PDF merging
# Chrome headless — already used for HTML→PDF above
```

### Workflow (proven on 265MB CHM → 180MB / 21,062-page PDF)

1. **Extract CHM with 7z** — `7zz x file.chm -o/tmp/chm_content -y`
   - Produces HTML files (GB2312 encoded), images, CSS, and a `.hhc` TOC file
   - Some internal files (#URLSTR, #STRINGS) may error — ignore, HTML content extracts fine
2. **Parse HHC** — GB2312-encoded XML-like file with `<OBJECT type="text/sitemap">` blocks containing `Name` (title) and `Local` (filename) params. Parse with regex to get ordered `(title, filename)` pairs.
3. **Batch convert** — For large docs (10,000+ pages), split into batches of ~300 pages:
   - Build one HTML file per batch with CSS `@page` styling and `page-break-before: always` per section
   - Convert each batch with Chrome headless (see "PDF Generation" section above)
   - **Do NOT try to convert a single 148MB HTML file** — Chrome hangs. Batching is essential.
4. **Merge PDFs** — Use `pypdf.PdfWriter().append()` to combine all batch PDFs into one.

### Encoding handling

CHM HTML files are typically GB2312. Read as bytes, decode with `gb2312` → fallback `gbk` → fallback `utf-8`. Replace `charset=gb2312` with `charset=utf-8` in the meta tag before re-rendering.

### Feishu (Lark) attachment download

To download a file attached to a Feishu message:
1. Get `tenant_access_token` via `POST /open-apis/auth/v3/tenant_access_token/internal` with `app_id` + `app_secret` (from `~/.hermes/.env`)
2. Get message content via `GET /open-apis/im/v1/messages/{message_id}` → parse JSON body for `file_key` and `file_name`
3. Download via `GET /open-apis/im/v1/messages/{message_id}/resources/{file_key}?type=file`
4. **Large file pitfall**: If the API returns `code: 234037` ("Downloaded file size exceeds limit"), use HTTP `Range` headers to download in 5MB chunks and concatenate. This works even when the single-request download is rejected.

See `references/chm-to-pdf.md` for the full conversion script and Feishu download details.

For direct use, run `scripts/chm_to_pdf.py <input.chm> <output.pdf>` — it handles extraction, batching, Chrome conversion, and merging end-to-end.

---

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
- For PDF generation: use Chrome headless (see "PDF Generation" section above)
