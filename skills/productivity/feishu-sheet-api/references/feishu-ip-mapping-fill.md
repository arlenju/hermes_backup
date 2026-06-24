# Feishu IP Mapping Cross-Reference — Session Notes

## Date
2026-06-08

## Goal
Fill #N/A cells in `Sheet1` of a firewall traffic spreadsheet by cross-referencing IP addresses against two reference tables in the same folder.

## Source Spreadsheets

| Role | URL | Token | Sheet ID | Rows |
|------|-----|-------|----------|------|
| **Target** | `Qmf2sLQe0h0eL1txbiKcaG8inOe` | Sheet1 | `1iPmja` | 10,344 |
| **Reference 1** | `MdJhs3r0dhGyKMt9BoEcBMA9njc` | Sheet1 | `1vnMBw` | 7,977 |
| **Reference 2** | `Rk5TsX0cghaCKntDfbUcH6t6nfg` | Sheet1 | `0GuWyE` | 9,800 |

## Columns (all 3 tables share the same layout)

```
A: SourceIP
B: 源地址用途 (Source Purpose) — mostly #N/A
C: 源地址管理员 (Source Admin) — mostly #N/A
D: DestinationIP
E: 目标地址用途 (Dest Purpose) — mostly #N/A
F: 目标地址管理员 (Dest Admin) — mostly #N/A
G: Protocol
H: DestinationPort
I: PolicyName
```

## Mapping Results

| Metric | Value |
|--------|-------|
| Source IPs with known purpose/admin | 3,357 |
| Destination IPs with known purpose/admin | 4,242 |
| Target cells that could be filled | 15,013 |
| Breakdown: 源地址用途 6,845 + 源地址管理员 3,340 + 目标地址用途 4,167 + 目标地址管理员 661 |

## Key API Details

### Reading the data
- All 3 sheets read in parallel: ~2 seconds each
- 17,777 reference rows + 10,344 target rows = ~28K rows total in memory
- No pagination needed (Feishu API returned full ranges)

### Data quality: `#UNSUPPORT VALUE`
Dropdown/combo-box cells return `{"type": "#UNSUPPORT VALUE"}` from the simple values API. This affected:
- Some cells in the reference tables (couldn't use those values for mapping)
- ALL empty/#N/A cells in the target table

The fix: use `isinstance(value, dict)` to detect and skip these.

### Write-back failure
Both PUT and POST write endpoints returned **91403 Forbidden** even after granting `sheets:spreadsheet` full scope. Probable cause: the Feishu app version wasn't re-published after adding the write scope, or the published version's authorization didn't propagate to the tenant access token.

## Working Code (read-only, mapping succeeds)

```python
import requests, json, time

# 1. Get token
resp = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    json={'app_id': app_id, 'app_secret': app_secret})
token = resp.json()['tenant_access_token']
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 2. Read all reference tables
all_ref = []
for ref_token, ref_sheet in [('TOKEN1', 'SHEET1'), ('TOKEN2', 'SHEET2')]:
    resp = requests.get(
        f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{ref_token}/values/{ref_sheet}!A:I',
        headers=headers)
    all_ref.extend(resp.json()['data']['valueRange']['values'][1:])

# 3. Build mappings
src_map, dst_map = {}, {}
for row in all_ref:
    if len(row) < 9: continue
    src_ip, dst_ip = row[0], row[3]
    # Skip #UNSUPPORT VALUE dicts
    src_p = row[1] if len(row)>1 and row[1] and not isinstance(row[1], dict) else None
    src_a = row[2] if len(row)>2 and row[2] and not isinstance(row[2], dict) else None
    dst_p = row[4] if len(row)>4 and row[4] and not isinstance(row[4], dict) else None
    dst_a = row[5] if len(row)>5 and row[5] and not isinstance(row[5], dict) else None
    if src_ip:
        cur = src_map.get(src_ip, [None, None])
        if src_p: cur[0] = src_p
        if src_a: cur[1] = src_a
        src_map[src_ip] = cur
    if dst_ip:
        cur = dst_map.get(dst_ip, [None, None])
        if dst_p: cur[0] = dst_p
        if dst_a: cur[1] = dst_a
        dst_map[dst_ip] = cur

# 4. Read and fill target
target_token = 'TARGET_TOKEN'
resp = requests.get(
    f'https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{target_token}/values/1iPmja!A:I',
    headers=headers)
rows = resp.json()['data']['valueRange']['values']
data_rows = rows[1:]

filled = 0
for ri, row in enumerate(data_rows):
    src_ip, dst_ip = row[0], row[3] if len(row)>3 else None
    if len(row)>1 and isinstance(row[1], dict) and src_ip in src_map and src_map[src_ip][0]:
        data_rows[ri][1] = src_map[src_ip][0]; filled+=1
    if len(row)>2 and isinstance(row[2], dict) and src_ip in src_map and src_map[src_ip][1]:
        data_rows[ri][2] = src_map[src_ip][1]; filled+=1
    if len(row)>4 and isinstance(row[4], dict) and dst_ip in dst_map and dst_map[dst_ip][0]:
        data_rows[ri][4] = dst_map[dst_ip][0]; filled+=1
    if len(row)>5 and isinstance(row[5], dict) and dst_ip in dst_map and dst_map[dst_ip][1]:
        data_rows[ri][5] = dst_map[dst_ip][1]; filled+=1

print(f"Filled {filled} cells")
```
