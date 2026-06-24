# Feishu Drive API

List folders, download files, and export documents from Feishu Drive (云盘).

## Required Permissions

| Scope | Level | What it enables |
|-------|-------|-----------------|
| `drive:drive:readonly` | Read | List files, download files, export documents |
| `drive:drive` | Read+Write | Also allows upload, delete, move |

**After adding permissions:** create new app version → publish → re-authorize at:
`https://open.feishu.cn/app/{app_id}/auth`

**⚠️ `drive:drive:readonly` often requires admin approval** in many Feishu tenants. If the API returns code `99991672`, the scope hasn't been granted yet.

## Authentication

Same as sheets — tenant_access_token via internal app:

```python
import requests
resp = requests.post("https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=15)
token = resp.json()["tenant_access_token"]
headers = {"Authorization": f"Bearer {token}"}
```

## List Files in Root / Folder

```python
BASE = "https://open.feishu.cn/open-apis"

# List root folder
r = requests.get(f"{BASE}/drive/v1/files",
    headers=headers,
    params={"page_size": 50}, timeout=30)
data = r.json()
# data["data"]["files"] → list of {name, token, type, ...}
# type: "file", "docx", "sheet", "folder"
```

### Pagination

```python
def list_all_files(token, folder_token=None):
    all_files = []
    page_token = None
    while True:
        params = {"page_size": 50}
        if folder_token:
            params["folder_token"] = folder_token
        if page_token:
            params["page_token"] = page_token
        r = requests.get(f"{BASE}/drive/v1/files",
            headers={"Authorization": f"Bearer {token}"},
            params=params, timeout=30)
        d = r.json()
        if d.get("code") != 0:
            break
        all_files.extend(d["data"]["files"])
        if not d["data"].get("has_more"):
            break
        page_token = d["data"].get("page_token")
    return all_files
```

## List Subfolder Contents

Use `folder_token` param:

```python
r = requests.get(f"{BASE}/drive/v1/files",
    headers=headers,
    params={"folder_token": folder_token, "page_size": 50}, timeout=30)
```

## Download a File (binary/uploaded files)

```python
r = requests.get(f"{BASE}/drive/v1/files/{file_token}/download",
    headers=headers, timeout=60)
# r.content → raw bytes
# r.headers.get("Content-Disposition") → filename
```

## Export a Docx Document to Markdown

Feishu docs (docx type) cannot be downloaded directly — they must be exported.

### Step 1: Submit export task

```python
import time
r = requests.post(f"{BASE}/drive/v1/export_tasks",
    headers=headers,
    json={
        "file_extension": "md",       # "md", "pdf", "docx", "txt", etc.
        "token": file_token,           # the docx document's token
        "type": "docx",                # source type: "docx", "sheet", "file"
        "sub_id": str(int(time.time()))  # unique idempotency key
    }, timeout=15)
d = r.json()
ticket = d["data"]["ticket"]  # polling key
```

### Step 2: Poll for completion

```python
for i in range(30):  # max 60s wait
    time.sleep(2)
    r = requests.get(f"{BASE}/drive/v1/export_tasks/{ticket}",
        headers=headers, timeout=15)
    d = r.json()
    status = d["data"]["status"]
    if status == 0:  # complete
        file_token_result = d["data"]["file_token"]
        dl = requests.get(f"{BASE}/drive/v1/export_tasks/file/{file_token_result}/download",
            headers=headers, timeout=60)
        return dl.text  # markdown content
    elif status in (1, 2):  # 1=processing, 2=queued
        continue
    else:
        break  # failed
```

### Supported export formats

| Format | `file_extension` |
|--------|-----------------|
| Markdown | `md` |
| PDF | `pdf` |
| Word | `docx` |
| Plain text | `txt` |

## File Types in Drive

| `type` value | Meaning | Can download directly? | Can export? |
|-------------|---------|----------------------|-------------|
| `file` | Uploaded binary file (PDF, image, zip, etc.) | ✅ Yes | ❌ No |
| `docx` | Feishu Doc (online document) | ❌ No | ✅ Yes (via export_tasks) |
| `sheet` | Feishu Spreadsheet | ❌ No | Use sheets API instead |
| `folder` | Directory | N/A | List contents with folder_token |

## Common Errors

| Code | Meaning | Fix |
|------|---------|-----|
| 99991672 | Missing scope | Add `drive:drive:readonly` permission, publish, re-authorize |
| 91403 | Forbidden | Scope not granted or token expired |
| 10001 | File not found | Token is wrong or file deleted |
| 10003 | Export not supported | This file type cannot be exported |

## Full Workflow: Drive → Obsidian

1. Get tenant token
2. List root folder → discover folder/file structure recursively
3. For each file:
   - `file` type: download raw bytes, save to local
   - `docx` type: submit export task → poll → download markdown
   - `sheet` type: skip (use sheets API separately)
4. Create matching directory structure under Obsidian vault
5. Save .md files for docx exports, note binary files with metadata

## ⚠️ Pitfalls

- **Export tasks are async** — must poll with 2s interval, up to ~60s for large docs
- **`sub_id` must be unique per request** — use `str(int(time.time()))` or UUID
- **Rate limit**: ~5 req/s for drive API, add `time.sleep(0.3)` between batch calls
- **Token expires in 2h** — for long exports, regenerate mid-way
- **No recursive listing endpoint** — must manually traverse folder tree
- **File names may contain special chars** — sanitize for filesystem use
