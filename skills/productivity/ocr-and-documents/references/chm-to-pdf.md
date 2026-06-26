# CHM → PDF Conversion — Detailed Reference

Session-proven on: Huawei "云园区网络解决方案 V100R022C00 & iMaster NCE-Campus V300R022C00" CHM (265MB → 180MB PDF, 21,062 pages, 10,637 TOC entries).

## 1. Feishu Attachment Download (with large-file chunking)

```python
import requests, os

# Get credentials from ~/.hermes/.env
app_id = "cli_xxx"  # from FEISHU_APP_ID
# read FEISHU_APP_SECRET from .env file

# Step 1: tenant access token
resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": app_id, "app_secret": app_secret}
)
tenant_token = resp.json()["tenant_access_token"]

# Step 2: get message to find file_key
message_id = "om_xxx"  # from HERMES_SESSION_KEY or message context
headers = {"Authorization": f"Bearer {tenant_token}"}
resp = requests.get(f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}", headers=headers)
body = json.loads(resp.json()["data"]["items"][0]["body"]["content"])
file_key = body["file_key"]
file_name = body["file_name"]

# Step 3: download — if single request fails with code 234037, use Range headers
url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}/resources/{file_key}"
params = {"type": "file"}
output_path = "/tmp/downloaded_file"
chunk_size = 5 * 1024 * 1024  # 5MB

start = 0
with open(output_path, "wb") as f:
    while True:
        end = start + chunk_size - 1
        r = requests.get(url, headers={**headers, "Range": f"bytes={start}-{end}"}, params=params)
        if r.status_code == 416:
            break  # done
        if r.status_code not in (200, 206):
            break  # error
        if not r.content:
            break
        f.write(r.content)
        if len(r.content) < chunk_size:
            break  # last chunk
        start += chunk_size
```

## 2. CHM Extraction

```bash
# 7z extracts the full HTML content (chmlib only gets internal structure files)
mkdir -p /tmp/chm_content
7zz x /tmp/file.chm -o/tmp/chm_content -y
# Errors on #URLSTR, #STRINGS etc. are normal — HTML/images extract fine
```

Typical output: 10,000+ HTML files (GB2312 encoded), 10,000+ images, one `.hhc` TOC file.

## 3. HHC Parsing (Table of Contents)

The `.hhc` file is GB2312 encoded, contains `<OBJECT type="text/sitemap">` blocks:

```python
import re, html

def parse_hhc(hhc_path):
    with open(hhc_path, 'r', encoding='gb2312', errors='replace') as f:
        content = f.read()
    entries = []
    objects = re.findall(r'<OBJECT[^>]*type="text/sitemap"[^>]*>(.*?)</OBJECT>', content, re.DOTALL)
    for obj in objects:
        name = re.search(r'name="Name"\s+value="([^"]*)"', obj)
        local = re.search(r'name="Local"\s+value="([^"]*)"', obj)
        if name and local:
            entries.append((html.unescape(name.group(1)), local.group(1)))
    return entries
```

## 4. Batch HTML → PDF Conversion

**Critical**: Do NOT build one giant HTML file (148MB) — Chrome headless hangs indefinitely. Split into batches of ~300 pages.

```python
def build_batch_html(entries, chm_dir, batch_num):
    """Build styled HTML for one batch of ~300 entries."""
    parts = ['''<!DOCTYPE html><html lang="zh-cn"><head><meta charset="utf-8">
<style>
@page { size: A4; margin: 2cm 1.5cm; }
body { font-family: "Microsoft YaHei", "PingFang SC", "Heiti SC", sans-serif; font-size: 10pt; line-height: 1.6; }
h1 { page-break-before: always; font-size: 18pt; color: #1a5276; }
h1:first-of-type { page-break-before: avoid; }
img { max-width: 100%; }
table { border-collapse: collapse; width: 100%; }
td, th { border: 1px solid #ccc; padding: 4px 8px; }
</style></head><body>''']
    
    for title, filename in entries:
        # Read with GB2312 → GBK → UTF-8 fallback
        raw = open(os.path.join(chm_dir, filename), 'rb').read()
        for enc in ['gb2312', 'gbk', 'utf-8']:
            try: content = raw.decode(enc); break
            except: continue
        else: content = raw.decode('utf-8', errors='replace')
        
        body_match = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
        body = body_match.group(1) if body_match else content
        parts.append(f'<div style="page-break-before: always;"><h1>{html.escape(title)}</h1>{body}</div>')
    
    parts.append('</body></html>')
    return ''.join(parts)

# Convert each batch with Chrome headless
def chrome_to_pdf(html_path, pdf_path):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.run([chrome, '--headless', '--disable-gpu', '--no-sandbox',
                    '--print-to-pdf=' + pdf_path, '--no-pdf-header-footer',
                    'file://' + html_path], timeout=120)
```

## 5. Merge PDFs

```python
from pypdf import PdfWriter

merger = PdfWriter()
for pdf_part in sorted(pdf_parts):
    merger.append(pdf_part)
merger.write(output_pdf)
merger.close()
```

## Performance Notes

- 265MB CHM → 10,637 pages → 36 batches of 300 → ~10 min total
- Each batch: 2-5MB HTML → 7-40MB PDF, ~15-30s per batch
- Chrome peak memory: ~5GB RAM for renderer process
- Final merged PDF: 180MB, 21,062 pages
- `weasyprint` was tried first but: (a) requires `pango` + `gobject` brew installs, (b) needs `DYLD_LIBRARY_PATH=/opt/homebrew/lib`, (c) far slower than Chrome for large docs
- `archmage`/`pychm` failed to compile on macOS ARM64 — don't bother
- `chm2pdf` package doesn't exist in pip registry
