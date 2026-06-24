# Cross-Sheet IP Lookup — Full Annotated Workflow

## Scenario

Fill IP→purpose/admin info in a target spreadsheet by cross-referencing one or more source tables.

## Step-by-Step

### 1. Determine actual data range first (critical — sheets often have 456K+ total rows but only 10K with data)

```python
# Read only column A to find the range
r = requests.get(f'{base}/values/{sheet_id}!A:A', headers=headers)
vals = r.json()['data']['valueRange']['values']
with_data = sum(1 for v in vals[1:] if v and v[0])  # minus header
total = len(vals) - 1
# Now you know the exact row count to process
```

Do NOT read B:F for all 456K rows — you'll timeout. Read only the data range.

### 2. Build IP→(purpose, admin) mapping from ALL reference tables

```python
# Target has format: SourceIP, 源地址用途, 源地址管理员, DestinationIP, 目标地址用途, 目标地址管理员, Protocol, Port, PolicyName
# Build separate maps for source and dest IPs
src_map, dst_map = {}, {}
for row in ref_rows:
    si, di = row[0], row[3] if len(row) > 3 else None
    sp = row[1] if isinstance(row[1], str) and row[1].strip() else None
    sa = row[2] if isinstance(row[2], str) and row[2].strip() else None
    dp = row[4] if isinstance(row[4], str) and row[4].strip() else None
    da = row[5] if isinstance(row[5], str) and row[5].strip() else None
    if si:
        cur = src_map.get(si, ['', ''])
        if sp: cur[0] = sp
        if sa: cur[1] = sa
        src_map[si] = cur
    if di:
        cur = dst_map.get(di, ['', ''])
        if dp: cur[0] = dp
        if da: cur[1] = da
        dst_map[di] = cur
```

### 3. Read + Fill + Clean in one pass

Only fill cells that are #UNSUPPORT VALUE or empty — never overwrite existing data.

```python
for ri, row in enumerate(data, 2):
    si = row[0] if row else None
    di = row[3] if len(row) > 3 else None
    
    for ci, col, ip, mapping, idx in [(1,'B',si,src_map,0), (2,'C',si,src_map,1), (4,'E',di,dst_map,0), (5,'F',di,dst_map,1)]:
        val = row[ci] if ci < len(row) else ''
        if isinstance(val, dict) or val == '#N/A' or val == '':
            if ip and ip in mapping and mapping[ip][idx]:
                data[ri][ci] = mapping[ip][idx]
            else:
                data[ri][ci] = ''  # NOT '#N/A' — that becomes UNSUPPORT VALUE
        elif isinstance(val, str):
            pass  # keep existing text
```

### 4. Write back in batches (4000 rows each)

```python
full = [header] + data
for start in range(0, len(full), 4000):
    end = min(start + 4000, len(full))
    resp = requests.put(f'{base}/values', headers=headers, json={'valueRange': {
        'range': f'{sheet_id}!A{start+1}:I{end}', 'values': full[start:end]
    }})
```

### 5. VERIFY before reporting (🔴 MANDATORY — do NOT skip)

**User rule: "做事情做了一定先自己检查，做完汇报"** — Never report without verifying first.

```python
# Read back sample cells to confirm write succeeded
r = requests.get(f'{base}/values/{sheet_id}!B6:B6', headers=headers)
actual = r.json()['data']['valueRange']['values'][0][0]
assert isinstance(actual, str) and actual not in ('', '#N/A'), f'Write failed: {actual}'

# Check a cell that should be empty
r = requests.get(f'{base}/values/{sheet_id}!B100:B100', headers=headers)
actual = r.json()['data']['valueRange']['values'][0][0]
assert actual == '', f'Expected empty, got {actual}'

# Count filled cells per column
r = requests.get(f'{base}/values/{sheet_id}!B:B', headers=headers)
vals = r.json()['data']['valueRange']['values'][1:]
filled = sum(1 for v in vals if v and isinstance(v[0], str) and v[0].strip())
print(f'Column B: {filled} filled cells')

# Only now report to user
```

### 6. Apply background color LAST (after all writes)

```python
# PUT /values clears all cell styles — apply AFTER final write
color = {'red': 0.86, 'green': 0.78, 'blue': 1.0}
for col in ['B','C','E','F']:
    for start in range(2, last_row+1, 2000):
        end = min(start + 1999, last_row)
        resp = requests.put(f'{base}/style', headers=headers, json={'appendStyle': {
            'range': f'{sheet_id}!{col}{start}:{col}{end}',
            'style': {'backgroundColor': color}
        }})
```

## One-IP Database (simpler variant)

If the target has columns [IP, IP用途, 管理员] (single IP per row, no source/dest split):

1. Build a flat `ip_map` from all reference tables (same logic but no source/dest distinction)
2. For each row, look up IP in `ip_map` and fill both B/C columns
3. Same write + verify + style workflow

## IP Database Sync Pattern (append new IPs)

When syncing an IP database table from a reference firewall log table:

1. **Build mapping** from the firewall log table — extract ALL unique SourceIPs and DestinationIPs with their purpose/admin
2. **Read existing IP database** — collect all existing IPs into a set
3. **Find new IPs** — iterate over the mapping; any IP not in the existing set is new
4. **Append** new rows to the bottom of the IP database table
5. **Fill gaps** — for existing rows with missing purpose/admin, overwrite from mapping
6. **Style** — apply purple background to newly added rows and filled cells

```python
# Step 3: Find new IPs
existing_ips = set(row[0] for row in db_rows if row and row[0])
new_rows = []
for ip, (purpose, admin) in ip_map.items():
    if ip not in existing_ips and (purpose or admin):
        new_rows.append([ip, purpose or '', admin or ''])

# Step 4: Append
start_row = len(db_rows) + 2  # after existing data + header
resp = requests.put(f'{base}/values', headers=headers, json={'valueRange': {
    'range': f'{sheet_id}!A{start_row}:C{start_row+len(new_rows)-1}',
    'values': new_rows
}})
```

## Bidirectional Round-Trip: Fill Target → Reverse-Fill IP DB

A common workflow: you fill a firewall-log-style target sheet (SourceIP/DestIP columns) from an IP database, then the user adds more data to the target and asks you to **reverse-fill** the IP DB with new IPs discovered in the target.

### Round-Trip Steps

**Phase 1 — Forward fill (target sheet ← IP DB):**
1. Build `ip_map` from IP DB (single-IP format: IP→[purpose, admin])
2. Read target sheet data (firewall log format: A=SourceIP, B=用途, C=管理员, D=DestinationIP, E=用途, F=管理员)
3. For each row, look up SourceIP and DestinationIP in `ip_map`
4. Only fill cells that are empty/placeholder (don't overwrite existing data)
5. Write back entire sheet in 4000-row batches
6. Verify by reading back sample cells

**Phase 2 — Reverse fill (IP DB ← target sheet):**
1. Build `ip_map` from the target sheet — extract ALL unique SourceIPs AND DestinationIPs with their purpose/admin. Merge duplicates: prefer non-empty values.
2. Read existing IP DB — collect all existing IPs into a set
3. **Fill existing rows:** For each IP DB row, if the admin is a placeholder ("待设置") and the target has a real admin for that IP, update it in-place
4. **Append new IPs:** Any IP in the target map not in the existing set → append as new rows at the bottom
5. Verify: check the updated placeholder cell, check first/last appended rows, count totals

```python
# Phase 2: Build IP map from target sheet (both source AND dest IPs)
ip_map = {}
for row in target_rows:
    if row[0] and isinstance(row[0], str):  # SourceIP
        ip = row[0].strip()
        purpose = row[1] if len(row) > 1 and isinstance(row[1], str) else ''
        admin = row[2] if len(row) > 2 and isinstance(row[2], str) else ''
        if purpose or admin:
            if ip not in ip_map:
                ip_map[ip] = [purpose, admin]
            else:
                if purpose and not ip_map[ip][0]: ip_map[ip][0] = purpose
                if admin and not ip_map[ip][1]: ip_map[ip][1] = admin
    if len(row) > 3 and row[3] and isinstance(row[3], str):  # DestinationIP
        ip = row[3].strip()
        purpose = row[4] if len(row) > 4 and isinstance(row[4], str) else ''
        admin = row[5] if len(row) > 5 and isinstance(row[5], str) else ''
        if purpose or admin:
            if ip not in ip_map:
                ip_map[ip] = [purpose, admin]
            else:
                if purpose and not ip_map[ip][0]: ip_map[ip][0] = purpose
                if admin and not ip_map[ip][1]: ip_map[ip][1] = admin

# Phase 2: Fill existing placeholder rows + find new IPs
existing_ips = set()
updates = []  # (row_num, new_admin)
for idx, row in enumerate(db_rows[1:], 2):
    if row and row[0]:
        ip = row[0].strip()
        existing_ips.add(ip)
        cur_admin = row[2] if len(row) > 2 and isinstance(row[2], str) else ''
        if ip in ip_map and ip_map[ip][1] and ip_map[ip][1] not in PLACEHOLDERS:
            if not cur_admin or cur_admin in PLACEHOLDERS:
                updates.append((idx, ip_map[ip][1]))

new_rows = []
for ip, (purpose, admin) in ip_map.items():
    if ip not in existing_ips:
        real_p = purpose if purpose and purpose not in PLACEHOLDERS else ''
        real_a = admin if admin and admin not in PLACEHOLDERS else ''
        if real_p or real_a:
            new_rows.append([ip, real_p, real_a])

# Write updates in-place, then append new rows at bottom
for row_num, new_admin in updates:
    requests.put(f'{base}/values', headers=headers, json={'valueRange': {
        'range': f'{sheet_id}!C{row_num}:C{row_num}', 'values': [[new_admin]]
    }})

start_row = len(db_rows) + 1  # after last data row
for start in range(0, len(new_rows), 500):
    end = min(start + 500, len(new_rows))
    requests.put(f'{base}/values', headers=headers, json={'valueRange': {
        'range': f'{sheet_id}!A{start_row+start}:C{start_row+end-1}',
        'values': new_rows[start:end]
    }})
```

### ⚠️ Pitfall: Source vs Dest IP may have different data for the same IP

When building the map from a firewall log, the same IP may appear as both SourceIP (with one purpose/admin) and DestinationIP (with a different purpose/admin). The merge logic above prefers the first non-empty value — but this can mask conflicts. If the user has a dedicated IP DB as the source of truth, always prefer IP DB data over target sheet data when both exist.

### ⚠️ Pitfall: New IPs carry their own "待设置" placeholders

When appending new IPs from the target sheet, the target may have "待设置" or "异常访问" as the admin value. These are NOT real admin names — filter them out with `PLACEHOLDERS` before appending. Only append rows where the admin is a real person's name.

## ⚠️ Critical: Chinese Placeholder "待设置" Must Be Checked Separately

When filling an IP database that has "待设置" (to be set) as admin values:

```python
# BAD — only checks if cell is empty/dict, misses "待设置" strings
if not cur_admin:
    # fills from mapping

# GOOD — also checks for Chinese placeholders
PLACEHOLDERS = {'待设置', '待定', 'N/A', 'null', '暂无'}
def needs_fill(val):
    if not val or isinstance(val, dict):
        return True
    s = str(val).strip()
    return not s or s in PLACEHOLDERS

if needs_fill(cur_admin) and ip in ip_map:
    # fill from mapping
```

**Pitfall:** The `needs_fill` check must be applied to BOTH the purpose column AND the admin column independently. A common bug is checking only the purpose column and assuming admin has the same status — they often differ (e.g., purpose is filled but admin is "待设置").
