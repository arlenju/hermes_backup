# Feishu multi-sheet location asset inventory example (2026-06-24)

## Scenario
User asked to summarize selected Feishu Sheet tabs from `网络设备资产位置信息统计（20260624更新）`: `国贸一座`, `国贸二座`, `国贸三期`, `国贸西楼`, `嘉里中心`, `国寿中心`.

## Durable workflow lessons

1. **Read each sheet by metadata width**
   - Query `/sheets/v3/spreadsheets/{token}/sheets/query`.
   - For each target title, use its `sheet_id`, `grid_properties.row_count`, and `grid_properties.column_count`.
   - Convert column count to the Excel rightmost column and read `A1:{right_col}{row_count}`.
   - Trim trailing all-empty rows locally.

2. **Treat selected tabs as peer detail tables, not one workbook-wide table**
   - Keep a `sheet名称` column in the combined detail.
   - Export both overall summaries and per-sheet summaries.
   - Reconcile totals: `sum(按Sheet汇总) == len(明细)`, and every overall grouping total must equal detail count.

3. **Common columns in this table family**
   - `公司/分公司`, `逻辑区域`, `大厦`, `存放位置`, `机架位置`, `U位`, `U数`, `设备型号`, `设备名称`, `设备管理IP地址`, `序列号`, `资产号`, `是否核验`, `设备状态`, date-like column (`投入日期` / `采购时间` / `采购日期` / `上架日期`).
   - Some tabs have extra blank columns and slightly different date column names.

4. **Counting口径 for rack-location sheets**
   - `1 row = 1 asset entry`.
   - `U数` is rack-space occupancy, NOT equipment count. Do not multiply row count by `U数`.
   - If no independent `堆叠数量/台数` field exists, do not do physical-count expansion.

5. **Brand/category inference when no vendor column exists**
   - These location sheets usually lack a `品牌/厂商` column. Infer only for summary convenience from `设备型号` + `设备名称`, while preserving raw model/name in details.
   - Useful mappings:
     - Cisco/思科: `C9300`, `C3850`, `C2960`, `WS-C`, `N9K`, `N3K`, `C3750`.
     - 华为/Huawei: `S5731`, `S5720`, `S6720`, `CE68`, `AR612`, `USG`.
     - H3C/新华三: `S5130`, `S5120`, `S5200`, `S6525`, `LS-`, `EWP-`, `WA66`, `MSR`, `SecPath`.
     - Juniper: `EX2200`, `EX2300`, `EX3400`, `EX4300`, `QFX`, `SSG-`.
     - Aruba: `Aruba`, `AP-315`, `AP-535`, `AP-555`, `IAP-`.
     - Fortinet: `Fortigate`, `Fortinet`, `FG-`, `FAP`.
     - F5: `F5`, `BIG-IP`; Palo Alto: `PA-`, `Palo`.
   - Label unmapped values as `其他/未识别`; do not pretend inferred labels are source data.

6. **Status cleanup pitfall**
   - In some rows, a date value appears under `设备状态` due to row-level column shifts or inconsistent source rows.
   - Do not count dates as statuses. Normalize date-looking statuses (`YYYY-MM-DD`) to `未填/日期误填`, preserve the original value in `原始设备状态`, and move/use it as date context when useful.

## Recommended workbook tabs

- `校验说明`
- `读取校验`
- `按Sheet汇总`
- `总体按状态`, `总体按分类`, `总体按品牌`, `总体按逻辑区域`, `总体按型号`
- `按Sheet状态`, `按Sheet核验`, `按Sheet分类`, `按Sheet品牌`, `按Sheet逻辑区域`, `按Sheet型号`, `按Sheet存放位置`
- `字段完整性`
- `清洗明细`

## Example result from this session

- Total selected assets: `2703`.
- By sheet: 国贸一座 `230`, 国贸二座 `1047`, 国贸三期 `240`, 国贸西楼 `803`, 嘉里中心 `83`, 国寿中心 `300`.
- Overall status after date cleanup: 在线 `1265`, 未填 `866`, 不在线 `220`, 闲置 `151`, 处置中 `121`, 未填/日期误填 `38`, 备件 `16`, 生产接入 `8`, 下线 `7`, 已下线 `5`, 在用 `4`, 可下线 `1`, 返厂维修中 `1`.
