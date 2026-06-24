# Feishu Spreadsheet API Access — Session Notes

## Date
2026-06-08

## Goal
Read a Feishu spreadsheet containing firewall traffic logs:
`https://rbnqidugqp.feishu.cn/sheets/Qmf2sLQe0h0eL1txbiKcaG8inOe`

## What Didn't Work

### 1. Headless Browser
- Navigated to Feishu sheet URL → redirected to `accounts.feishu.cn/accounts/page/login`
- QR code rendered as HTML Canvas, screenshots were blank (headless Chromium issue)
- QR code data URL was extractable from canvas via `canvas.toDataURL()`, but user couldn't scan it (different browser session)
- **Lesson:** Headless browser can't access private Feishu resources. Use API.

### 2. macOS Computer Use (not available)
- `computer_use` toolset is enabled but `cua-driver` not installed
- Would require setup + accessibility permissions
- **Lesson:** When available, this could drive Safari which has the user's Feishu session

## What Worked: Feishu REST API

### Initial Attempt — Permission Denied
```
GET /open-apis/sheets/v3/spreadsheets/{token}/sheets/query
→ 99991672: "Access denied. One of the following scopes is required: 
  [sheets:spreadsheet, drive:drive, sheets:spreadsheet:readonly, 
   drive:drive:readonly, sheets:spreadsheet:read]"
```

**Fix:** User went to Feishu Developer Console and granted `sheets:spreadsheet:readonly` scope.

### Successful Access
```
GET /open-apis/sheets/v3/spreadsheets/{token}/sheets/query
→ 3 sheets found: 防火墙流量日志 (135K rows), Sheet1 (10K rows), 导出计数_PolicyName (200 rows)

GET /open-apis/sheets/v2/spreadsheets/{token}/values/{sheet_id}!A1:T6
→ Data returned as 2D array in data.valueRange.values
```

### Data Discovered

**Sheet 1: 防火墙流量日志** (135,765 rows × 5 columns)
| Column | Sample |
|--------|--------|
| SourceIP | 10.93.75.29, 10.119.207.226 |
| DestinationIP | 10.108.10.57, 10.40.198.17 |
| Protocol | tcp, udp |
| DestinationPort | 8080, 443, 8090 |
| PolicyName | VDI网段访问10.108网段策略, Wireless-to-IOA-5 |

**Sheet 2: Sheet1** (10,344 rows × 9 columns)
Extra columns: 源地址用途, 源地址管理员, 目标地址用途, 目标地址管理员
(These dropdown fields return `#UNSUPPORT VALUE` from the API)

**Sheet 3: 导出计数_PolicyName** (200 rows × 3 columns)
Aggregated counts: PolicyName, 计数, 占比
Top: CLSL-GMPC-GM (2866, 27.7%), CLSL-GMPC-NFZX (1935, 18.7%)

## Working Python Template

```python
import requests, json
from collections import Counter

app_id = 'cli_xxx'
app_secret = 'your_secret'

# Get token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret})
token = resp.json()['tenant_access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Read sheet
spreadsheet_token = 'Qmf2sLQe0h0eL1txbiKcaG8inOe'
resp = requests.get(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/0fUaAr!A1:E100',
    headers=headers)
rows = resp.json()['data']['valueRange']['values']
```

## Update: Write-back Now Working (2026-06-08 Session)

After correctly adding `sheets:spreadsheet` (full, not readonly), publishing a new version, and re-authorizing, write-back succeeded:

- **3 batches** of 4K rows each (10,344 total rows × 9 columns)
- Key fixes: use `sheet_id` (e.g. `1iPmja`) not sheet name (`Sheet1`); convert all dict values to plain strings first
- Cell styling also works via `appendStyle` wrapper

## Expanded Cross-Reference (3 tables, 23K rows)

Added a third reference table (新表6, `IToYsCHGyhWIEotF8JLcQpvinsb`, 5,189 rows) with the same schema.
Combined with the original two tables, it yielded:
- Source IP mappings: 3,583 (up from 3,357)
- Dest IP mappings: 5,285 (up from 4,242)
- Additional cells filled: 688

## Key Takeaway for #N/A Remaining

Even with three reference tables totaling 23K rows, ~50% of target IPs still had no mapping. The remaining #N/A isn't a bug — the reference tables simply don't contain those IPs. Always report match rate so the user can decide if more data sources are needed.
1. Feishu app credentials work for API access when scopes are granted
2. Sheets API v3 for metadata, v2 for cell values
3. Large datasets (100K+ rows) are fine to read in Python
4. Dropdown/custom fields return `#UNSUPPORT VALUE` — API limitation
5. Always get a fresh tenant token (expires ~2 hours)
