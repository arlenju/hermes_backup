# Feishu network asset inventory example — 2026-06-24

Use this as a compact pattern for Feishu-hosted network asset sheets with many columns and mixed vendor spellings.

## Source shape

- Feishu spreadsheet title: `网络设备资产位置信息统计（20260624更新）`
- Detail sheet: `非金系统网络资产清单`, sheet_id `qUu4hu`
- Metadata reported 9035 rows × 56 columns, so the full read range was `A1:BD9035`.
- Row 1 was the header; 9034 non-empty detail rows.
- Important columns included: `资产标签号`, `资产机身号`, `资产名称`, `资产类别`, `品牌`, `配置规格`, `资产状态`, `地点类型`, `存放地点名称`, `位置详细描述`, `管理部门`, `资产管理人`, `资产卡片状态`, `供应商`, value/warranty fields.

## Lessons

1. **Read full width from metadata, not A:Z.** An initial A:Z read missed columns AA:BD. Query `grid_properties.column_count` and convert to Excel label (56 → BD).
2. **Counting口径:** this sheet had no independent `堆叠数量/台数` column, so report `资产条目数` only (`1 row = 1 asset`). Do not infer physical devices from text in `配置规格` unless explicitly requested.
3. **Brand normalization is useful but preserve raw labels.** Normalize common variants for summary only:
   - `CISCO` / `CICSO` / `思科` → `Cisco/思科`
   - `华为` / `Huawei` → `华为/Huawei`
   - `H3C` / `新华三` → `H3C/新华三`
   - `DELL` / `Dell` / `戴尔` → `Dell/戴尔`
   - `fortigate` / `fortinet` → `Fortinet`
   Keep `按原始品牌` and `清洗明细` sheets so the user can audit.
4. **Useful workbook tabs:** `校验说明`, `按归一品牌`, `按原始品牌`, `按资产小类`, `按资产状态`, `按卡片状态`, `按存放地点`, `按详细位置`, `按管理人`, `按品牌型号`, `按地点品牌`, `字段完整性`, `清洗明细`.
5. **Self-check before reporting:** verify every grouped total sums to the detail row count, then re-open the exported XLSX and check sheet names + totals.

## Example headline results from this source

- Detail rows: 9034
- Asset status: 正常使用 8955, 闲置 79
- Card status: 可用 9033, 禁用 1
- Top normalized brands: Cisco/思科 2084; 华为/Huawei 1815; 未填 1142; H3C/新华三 905; Avaya 696.
- Top asset classes: 网络交换机 4089; 无线网络设备 1322; 电话终端 1043; 服务器 696; 配件/模块/软授权 405.

These numbers are session-specific examples; future runs must recalculate from the live sheet.
