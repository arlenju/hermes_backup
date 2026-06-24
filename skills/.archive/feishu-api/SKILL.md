---
name: feishu-api
description: "Access Feishu (飞书) data via the REST API — read spreadsheets, query sheet structure, fetch cell values, and manage API permissions. Complements the built-in feishu_doc_read tool for document access."
version: 1.3.0
author: agent
platforms: [macos, linux]
metadata:
  hermes:
    tags: [feishu, lark, api, spreadsheet, sheets, data]
    category: productivity
    related_skills: [voice-pipeline, feishu-sheet-api]
---

# Feishu API — Spreadsheet & Data Access

Access Feishu data programmatically via the Feishu Open API. Use when you
need to read spreadsheet content, query sheet structure, or fetch data
that the built-in `feishu_doc_read` tool (docs only) cannot reach.

## Prerequisites

The Feishu gateway app must have the necessary API scopes (permissions)
enabled in the Feishu Developer Console.

### Required Scopes

| Scope | Purpose | Where to add |
|-------|---------|-------------|
| `sheets:spreadsheet:readonly` | Read spreadsheet content | https://open.feishu.cn/app/<APP_ID>/auth |
| `drive:drive:readonly` | Read Drive files | Same URL |

App ID is in `~/.hermes/.env` as `FEISHU_APP_ID`.

### Credentials

Credentials live in `~/.hermes/.env`:
```
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_DOMAIN=feishu
```

## Workflow: Read a Spreadsheet

### Step 1 — Get Tenant Access Token

```python
import requests
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={
    'app_id': app_id,
    'app_secret': app_secret
})
token = resp.json()['tenant_access_token']
```

The token expires in ~7200 seconds. Re-fetch for each session.

### Step 2 — Discover Sheet Structure

```python
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
spreadsheet_token = 'xxx'  # From URL: sheets/<TOKEN>
resp = requests.get(
    f'https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query',
    headers=headers
)
```

Returns sheet list with `sheet_id`, `title`, `row_count`, `column_count`.

### Step 3 — Read Cell Values

```python
resp = requests.get(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}!A1:T10',
    headers=headers
)
```

Range format: `{sheet_id}!{start_cell}:{end_cell}` (e.g. `0fUaAr!A1:T6`).

Returns a 2D array in `data.valueRange.values`.

## Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| `99991672` | Missing API scope | Add `sheets:spreadsheet:readonly` in dev console, publish, re-authorize |
| `91403` | Forbidden | Missing or unpublished scope. Ensure `sheets:spreadsheet` (not readonly) is added, published, and re-authorized |
| `90202` | Invalid range | Use `"B6:B6"` format, not `"B6"` for single cells |
| `9499` | Missing `appendStyle` wrapper | For cell styling, wrap in `{"appendStyle": {"range": ..., "style": ...}}` |
| `#UNSUPPORT VALUE` (dict) | Dropdown/custom field type | API v2 simple values returns `{"type": "#UNSUPPORT VALUE"}` for combo-box/dropdown cells. **Must convert to plain string before writing** to avoid "invalid cell type" error. |

## Write Operations — ✅ VERIFIED WORKING

**Writing back to Feishu spreadsheets via the tenant_access_token DOES work** after the correct permissions, publishing, and re-authorization flow is followed.

### Prerequisites for write access

1. **Add the `sheets:spreadsheet` scope** (NOT `readonly`) in the Feishu Developer Console → app → Permissions → Sheets
2. **Create a new version** in **「版本管理」** (Version Management)
3. **Publish** the version
4. **Re-authorize** at `https://open.feishu.cn/app/<APP_ID>/auth` — the old token inherits old scopes even after publishing

### Early-failure gotchas (observed in production)

| Symptom | Root cause | Fix |
|---------|-----------|-----|
| 91403 Forbidden on PUT | Scope not published/re-authorized | Follow steps 2-4 above |
| 91403 Forbidden again | Token still has old scopes | User must re-visit auth URL |
| "invalid cell type" | Dict objects (`#UNSUPPORT VALUE`) in values matrix | Convert all cells to plain strings before writing |
| 90202 "wrong range" | Using sheet name (`Sheet1`) instead of sheet ID (`1iPmja`) | Always use the sheet_id from metadata query |

### Write API reference

For full write examples (batch range write, single-column write, cell styling), see the **`feishu-sheet-api`** skill — it has detailed, tested code for all write operations including `appendStyle` formatting.

⚠️ **Note:** `feishu-api` and `feishu-sheet-api` overlap significantly. Consolidation is pending via the curator.

### What IS tested and works (this session)

- ✅ Reading any spreadsheet that the app has scope for
- ✅ Reading multiple spreadsheets and cross-referencing
- ✅ Building mapping dictionaries in Python from 10K+ rows
- ✅ Writing full sheet data back (10,344 rows × 9 columns, 3 batches of 4K)
- ✅ Single-column write via contiguous runs (B/C/E/F columns)
- ✅ Cell styling via `appendStyle` API (background color)
- ❌ Drive API (`drive:drive:readonly`) — requires admin approval in most tenants

## Cross-Reference & Fill Pattern — PROVEN WORKFLOW

A common task: fill missing cells (e.g. #N/A / dropdown fields) in one
spreadsheet by cross-referencing IP addresses (or other keys) against
other tables in the same folder.

### Full Workflow (read-only, mapping succeeds)

1. **Read the target sheet** that has #N/A cells needing fill:
   ```python
   resp = requests.get(
       f'{base}/sheets/v2/spreadsheets/{target_token}/values/{sheet_id}!A:I',
       headers=headers
   )
   rows = resp.json()['data']['valueRange']['values'][1:]  # skip header
   ```

2. **Read reference tables** with the mapping data:
   ```python
   for ref_sid, ref_sheet in [('token1', 'sheet1'), ('token2', 'sheet2')]:
       resp = requests.get(f'{base}/sheets/v2/spreadsheets/{ref_sid}/values/{ref_sheet}!A:I', headers=headers)
       all_ref.extend(resp.json()['data']['valueRange']['values'][1:])
   ```

3. **Build lookup dictionaries** — works with 10K+ entries:
   ```python
   src_map, dst_map = {}, {}
   for row in all_ref:
       if len(row) < 9: continue
       src_ip = row[0]
       # Skip cells that are dicts (#UNSUPPORT VALUE)
       src_purpose = row[1] if row[1] and not isinstance(row[1], dict) else None
       if src_ip and src_purpose:
           src_map.setdefault(src_ip, [None, None])[0] = src_purpose
   ```

4. **Fill the target data in memory** (this session: 15,013 cells across 10,344 rows):
   ```python
   for ri, row in enumerate(data_rows):
       src_ip = row[0]
       if isinstance(row[1], dict) and src_ip in src_map and src_map[src_ip][0]:
           data_rows[ri][1] = src_map[src_ip][0]  # fill source purpose
   ```

5. **Attempt to write back** — see "Write Operations" section above for results.

### What's needed for the mapping table

Reference tables should have the same column structure as the target:
`SourceIP | 源地址用途 | 源地址管理员 | DestinationIP | 目标地址用途 | 目标地址管理员 | ...`

### Real-world scale (this session, verified working)

| Metric | Value |
|--------|-------|
| Reference tables used | 3 (2 original + 1 added later = 23K rows total) |
| Source IP mappings built | 3,583 (from 3 combined tables) |
| Destination IP mappings built | 5,285 |
| Target rows processed | 10,344 |
| Cells filled (total) | ~15,700 |
| Fill rate (source columns) | 3,506/10,344 (34%) |
| Fill rate (dest columns) | 4,987/10,344 (48%) |
| #N/A remaining | ~24K (IPs not in any reference table) |
| Write-back method | Full A-I range in 3 batches of 4K rows |
| Write-back success | ✅ (3 batches, 10,344 rows) |

## Common Patterns

### Summary Statistics

After reading raw data, aggregate with Python:
```python
from collections import Counter
counter = Counter(row[4] for row in rows[1:])  # e.g. PolicyName column
```

### Large Datasets

For sheets with 100K+ rows, use paginated queries or aggregate at the API
level. Python-side processing is fine for up to ~200K rows of text data.

### URL Parsing

Extract tokens from Feishu sheet URLs:

| URL part | Where | Example |
|----------|-------|---------|
| `spreadsheet_token` | `/sheets/<TOKEN>` | `Qmf2sLQe0h0eL1txbiKcaG8inOe` |
| `sheet_id` | Query `?sheet=<SHEET_ID>` or from metadata query | `1iPmja` |

```python
# From full URL
url = "https://rbnqidugqp.feishu.cn/sheets/Qmf2sLQe0h0eL1txbiKcaG8inOe?sheet=1iPmja"
spreadsheet_token = url.split('/sheets/')[1].split('?')[0]  # Qmf2sLQe0h0eL1txbiKcaG8inOe
```

For folder URLs, extract the folder token:
```python
folder_url = "https://rbnqidugqp.feishu.cn/drive/folder/LFwbfdgR7lbY0jdGlDXcKsBInhd"
folder_token = folder_url.split('/folder/')[1]  # LFwbfdgR7lbY0jdGlDXcKsBInhd
```

## Reference Files

- `references/feishu-spreadsheet-access.md` — Full session transcript with
  exact API calls, error codes encountered, and working example against a
  real firewall traffic log spreadsheet.
