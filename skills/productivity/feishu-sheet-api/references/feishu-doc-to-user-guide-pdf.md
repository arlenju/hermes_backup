# Feishu Doc → User-Friendly PDF Guide

Use this when the user shares a Feishu/Lark Docx and asks to make a simplified, user-readable guide as a PDF.

## Recommended workflow

1. **Extract source text via Docx API first**
   - Prefer `GET /open-apis/docx/v1/documents/{doc_token}/raw_content` with a tenant access token.
   - This may succeed even when Drive export to `docx/pdf` returns `1069902 no permission` or markdown export is unsupported.
   - Also query `GET /docx/v1/documents/{doc_token}` for the title/revision when useful.

2. **Rewrite for ordinary users**
   - Convert policy-heavy text into: when to apply, what to prepare, normal/emergency process, execution time, common scenarios, verification, troubleshooting, and checklist.
   - Preserve operationally important facts: cutoff times, change windows, email addresses, high-risk ports, exceptions, and safety responsibilities.
   - Avoid exposing raw API details or long original-policy wording in the final user PDF.

3. **Render PDF locally**
   - Markdown → PDF can be done with Python + PIL when pandoc/reportlab/weasyprint are absent.
   - Use macOS CJK fonts such as `/System/Library/Fonts/Hiragino Sans GB.ttc` or `/System/Library/Fonts/STHeiti Medium.ttc`.
   - If PIL PDF save raises `KeyError: 'JPEG'`, import `PIL.JpegImagePlugin` before saving.

4. **Self-verify before sending**
   - Check the file exists, has `%PDF-` header, ends with `%%EOF`, has non-trivial size, and `file` reports a PDF with expected page count.
   - Verify the source Markdown contains the important keywords from the source (times, emails, high-risk ports, checklist items) before delivery.

## Tenant token snippet

```python
import os, requests
BASE = 'https://open.feishu.cn/open-apis'

def load_env_key(name):
    with open(os.path.expanduser('~/.hermes/.env'), encoding='utf-8') as f:
        for line in f:
            s = line.strip()
            if s.startswith(name + '='):
                return s.split('=', 1)[1].strip().strip('"').strip("'")
    raise RuntimeError(name)

app_id = load_env_key('FEISHU_APP_ID')
app_secret = load_env_key('FEISHU_APP_SECRET')
r = requests.post(BASE + '/auth/v3/tenant_access_token/internal',
                  json={'app_id': app_id, 'app_secret': app_secret}, timeout=20)
r.raise_for_status()
token = r.json()['tenant_access_token']
headers = {'Authorization': 'Bearer ' + token}
raw = requests.get(BASE + f'/docx/v1/documents/{DOC_TOKEN}/raw_content',
                   headers=headers, timeout=30).json()['data']['content']
```

## Pitfalls

- Feishu Drive export `file_extension=md` may be rejected; do not depend on markdown export for Docx.
- Drive export can require permissions that raw Docx content does not; try raw content before asking the user for permissions.
- The deliverable should be the PDF attachment alone if the user asks “做成pdf单发给我”; keep accompanying text minimal.
