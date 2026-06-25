---
name: spreadsheet-asset-inventory
description: Analyze Excel/CSV asset inventories and produce verified counts by vendor/model/type/site, with explicit counting口径 and exported summary workbooks.
---

# Spreadsheet Asset Inventory

Use this when the user asks to count, classify, or summarize asset/device inventories from Excel/CSV files, especially network equipment资产台账 with fields like 厂商、型号、设备类型、IP、序列号、堆叠数量、位置、区域。

## Workflow

1. **Find and confirm the source file**
   - Search likely project/user folders for the named site/project (e.g. `国贸`, `设备`, `资产`, `清单`).
   - If multiple candidate sheets/files exist, inspect workbook sheet names and first rows before choosing.
   - Prefer the sheet that has actual asset rows and columns such as `厂商`, `设备型号`, `设备名称`, `管理IP`, `序列号`.

2. **Inspect workbook structure before computing**
   - Print sheet names, each candidate sheet shape, headers, and sample rows.
   - Detect extra header rows, merged-ish layouts, blank separator rows, duplicate columns, and summary sheets that should not be treated as source detail.

3. **Normalize fields**
   - Strip whitespace on key columns.
   - Treat empty vendor/model/name/IP carefully; report dropped/unknown rows rather than silently ignoring.
   - Preserve original labels; do not over-normalize vendor/model names unless the user asks (e.g. `EX3400` and `EX3400.1` should remain separate unless merged intentionally).

4. **Define counting口径 explicitly**
   - Distinguish **资产条目数** (spreadsheet rows/assets) from **折算台数** (physical devices).
   - If there is a stack/count column such as `堆叠数量`, compute both:
     - row count = one record per row;
     - physical count = numeric stack count when present, otherwise 1.
   - In the final answer, state which figure is being reported and include both when useful.

5. **Aggregate and verify**
   - Typical outputs:
     - by vendor: `厂商 -> 资产条目数, 折算台数`
     - by vendor + model: `厂商, 设备型号 -> 资产条目数, 折算台数`
     - optionally by device type/site/building.
   - Verify totals reconcile:
     - detail row count == sum of group row counts;
     - physical count == sum of grouped physical counts.
   - Print/record validation numbers before reporting.

6. **Export a usable artifact**
   - Create an `.xlsx` summary workbook with sheets:
     - `校验说明`
     - `按厂商汇总` / `按归一品牌` when brand spellings vary
     - `按厂商型号汇总` / `按品牌型号`
     - `按设备类型/资产小类`
     - `按位置/存放地点`
     - `字段完整性`
     - `明细` / `清洗明细`
   - Also use `.csv` only as a secondary format if the user needs quick import.
   - Return the exported file via `MEDIA:/absolute/path` when in Feishu/Lark.

7. **For Feishu Sheet URLs, read the actual full sheet width**
   - Parse both `spreadsheet_token` and `sheet_id` from the URL, then query sheet metadata.
   - Use `grid_properties.column_count` to compute the real rightmost column (e.g. 56 → `BD`) and read `A1:{right_col}{row_count}`.
   - Do **not** inspect only `A:Z`; asset tables may have important fields after column Z (e.g. supplier, original value, warranty dates).
   - Still trim trailing all-empty rows after reading, and reconcile all group totals back to the detail count.

## Python pattern

```python
import pandas as pd
from pathlib import Path

src = Path('/path/to/assets.xlsx')
df = pd.read_excel(src, sheet_name='Sheet1')

for col in ['区域','厂商','设备型号','名称（不动）','管理IP','设备类型','堆叠数量']:
    if col in df.columns:
        df[col] = df[col].astype('string').str.strip()

detail = df[df['区域'].fillna('').str.contains('国贸', na=False)].copy()
detail['堆叠数量_num'] = pd.to_numeric(detail['堆叠数量'], errors='coerce')
detail['统计台数'] = detail['堆叠数量_num'].fillna(1).astype(int)

by_vendor = detail.groupby('厂商', dropna=False).agg(
    资产条目数=('名称（不动）','count'),
    统计台数=('统计台数','sum'),
).reset_index().sort_values('统计台数', ascending=False)

by_model = detail.groupby(['厂商','设备型号'], dropna=False).agg(
    资产条目数=('名称（不动）','count'),
    统计台数=('统计台数','sum'),
).reset_index().sort_values(['厂商','统计台数','设备型号'], ascending=[True,False,True])

assert int(by_vendor['统计台数'].sum()) == int(detail['统计台数'].sum())
assert int(by_model['统计台数'].sum()) == int(detail['统计台数'].sum())
```

## Pitfalls

- Do **not** answer from a summary sheet alone unless the user explicitly wants the existing summary; compute from detail rows when possible.
- Do **not** conflate row count with physical count when stack columns exist.
- Avoid shell `&` in inline Python text or table labels when terminal safety filters may interpret it as backgrounding; use words like `Vendor model counts` instead of `Vendor+model counts` if needed.
- If pandas cannot read `.xlsx` because `openpyxl` is missing, install it in the active runtime venv (`python3 -m pip install openpyxl`) and rerun the inspection.
- User values data accuracy over formatting: inspect, calculate, export, and validate before reporting.

## References

- `references/guomao-network-assets-2026.md` — example口径 and output structure from a 国贸网络设备资产统计 session.
- `references/feishu-network-assets-20260624.md` — Feishu wide-sheet inventory example: read full width from metadata, normalize vendor names while preserving raw labels, export multi-tab workbook, and verify grouped totals.
- `references/feishu-multisheet-location-assets-20260624.md` — Feishu multi-tab location/rack asset inventory example: selected sheet titles, per-sheet + overall summaries, rack `U数` counting pitfall, inferred brand/category, and date-in-status cleanup.
