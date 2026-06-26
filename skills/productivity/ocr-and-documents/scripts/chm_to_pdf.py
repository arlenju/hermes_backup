#!/usr/bin/env python3
"""
CHM → PDF batch converter.
Usage: python3 chm_to_pdf.py <input.chm> <output.pdf>

Extracts CHM with 7z, parses HHC table of contents, builds batch HTML files,
converts each batch with Chrome headless, then merges all PDFs.
"""

import os, re, sys, html, subprocess, shutil

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BATCH_SIZE = 300

def parse_hhc(hhc_path):
    with open(hhc_path, 'r', encoding='gb2312', errors='replace') as f:
        content = f.read()
    entries = []
    for obj in re.findall(r'<OBJECT[^>]*type="text/sitemap"[^>]*>(.*?)</OBJECT>', content, re.DOTALL):
        name = re.search(r'name="Name"\s+value="([^"]*)"', obj)
        local = re.search(r'name="Local"\s+value="([^"]*)"', obj)
        if name and local:
            entries.append((html.unescape(name.group(1)), local.group(1)))
    return entries

def read_html(path):
    raw = open(path, 'rb').read()
    for enc in ['gb2312', 'gbk', 'utf-8']:
        try: return raw.decode(enc)
        except: continue
    return raw.decode('utf-8', errors='replace')

def extract_body(content):
    m = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
    return m.group(1) if m else content

def build_batch_html(entries, chm_dir, is_first):
    parts = [f'''<!DOCTYPE html><html lang="zh-cn"><head><meta charset="utf-8">
<style>
@page {{ size: A4; margin: 2cm 1.5cm; }}
body {{ font-family: "Microsoft YaHei","PingFang SC","Heiti SC",sans-serif; font-size: 10pt; line-height: 1.6; color: #333; }}
h1 {{ page-break-before: always; font-size: 18pt; color: #1a5276; border-bottom: 2px solid #1a5276; padding-bottom: 5px; }}
h1:first-of-type {{ page-break-before: avoid; }}
h2 {{ font-size: 14pt; color: #2874a6; }} h3 {{ font-size: 12pt; color: #2e86c1; }}
img {{ max-width: 100%; height: auto; }}
table {{ border-collapse: collapse; width: 100%; }} td,th {{ border: 1px solid #ccc; padding: 4px 8px; }}
</style></head><body>''']
    if is_first:
        parts.append('<div style="text-align:center;padding-top:300px;"><h1 style="page-break-before:avoid;font-size:24pt;border:none;">Document</h1></div>')
    for title, filename in entries:
        body = extract_body(read_html(os.path.join(chm_dir, filename)))
        parts.append(f'<div style="page-break-before:always;"><h1>{html.escape(title)}</h1>{body}</div>')
    parts.append('</body></html>')
    return ''.join(parts)

def chrome_to_pdf(html_path, pdf_path):
    r = subprocess.run([CHROME, '--headless', '--disable-gpu', '--no-sandbox',
                        '--disable-dev-shm-usage', '--print-to-pdf=' + pdf_path,
                        '--no-pdf-header-footer', 'file://' + html_path],
                       capture_output=True, timeout=120)
    return os.path.exists(pdf_path)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 chm_to_pdf.py <input.chm> <output.pdf>")
        sys.exit(1)
    
    chm_file, output_pdf = sys.argv[1], sys.argv[2]
    work_dir = f"/tmp/chm_work_{os.getpid()}"
    extract_dir = os.path.join(work_dir, "content")
    parts_dir = os.path.join(work_dir, "parts")
    os.makedirs(parts_dir, exist_ok=True)
    
    # Step 1: Extract CHM
    print(f"Extracting {chm_file}...")
    os.makedirs(extract_dir, exist_ok=True)
    subprocess.run(['7zz', 'x', chm_file, '-o', extract_dir, '-y'], capture_output=True)
    
    # Step 2: Find and parse HHC
    hhc_files = []
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            if f.endswith('.hhc'):
                hhc_files.append(os.path.join(root, f))
    if not hhc_files:
        print("ERROR: No .hhc file found in CHM")
        sys.exit(1)
    
    entries = parse_hhc(hhc_files[0])
    valid = [(t, f) for t, f in entries if os.path.exists(os.path.join(extract_dir, f))]
    print(f"TOC entries: {len(valid)}")
    
    # Step 3: Batch convert
    total_batches = (len(valid) + BATCH_SIZE - 1) // BATCH_SIZE
    pdf_parts = []
    
    for i in range(total_batches):
        start = i * BATCH_SIZE
        batch = valid[start:start + BATCH_SIZE]
        html_path = os.path.join(parts_dir, f"batch_{i:04d}.html")
        pdf_path = os.path.join(parts_dir, f"batch_{i:04d}.pdf")
        
        print(f"[{i+1}/{total_batches}] Batch {start}-{start+len(batch)-1}...")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(build_batch_html(batch, extract_dir, i == 0))
        
        if chrome_to_pdf(html_path, pdf_path):
            pdf_parts.append(pdf_path)
            print(f"  ✅ {os.path.getsize(pdf_path)/1024/1024:.1f} MB")
        else:
            print(f"  ❌ Failed")
        os.remove(html_path)
    
    # Step 4: Merge
    print(f"\nMerging {len(pdf_parts)} PDFs...")
    try:
        from pypdf import PdfWriter
    except ImportError:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pypdf'], check=True)
        from pypdf import PdfWriter
    
    merger = PdfWriter()
    for p in pdf_parts:
        merger.append(p)
    merger.write(output_pdf)
    merger.close()
    
    print(f"\n✅ {output_pdf} ({os.path.getsize(output_pdf)/1024/1024:.1f} MB)")
    shutil.rmtree(work_dir, ignore_errors=True)

if __name__ == "__main__":
    main()
