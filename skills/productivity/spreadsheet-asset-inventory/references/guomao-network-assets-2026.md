# 国贸网络设备资产统计示例（2026）

This reference captures the reusable counting口径 from a session analyzing `/Users/jushuai/My_Project/11/国贸设备替换清单-2026.xlsx`.

## Workbook structure observed

Sheets included:

- `Sheet1` — primary detail table for existing devices, 183 rows and columns such as `区域`, `设备类型`, `名称（不动）`, `管理IP`, `厂商`, `设备型号`, `堆叠数量`, `序列号`.
- `备机统计` — spare inventory, separate asset class.
- `总表-涵盖所有3850` — replacement project detail for 3850-class devices.
- `计划批次` — migration batches, not asset detail.
- `已替换设备清单` — replacement completed list.
- `设备数量信息` — human-maintained summary, useful for cross-check but not primary source.
- `小网设备清单` — separate small-network inventory.

## Counting口径 used

For `Sheet1`:

- Valid 国贸 rows: 183.
- `设备类型` split: 168 switches, 15 routers.
- Vendor rows: Cisco 171, Juniper 12.
- `堆叠数量` was non-empty for some rows. For reporting physical devices:
  - numeric `堆叠数量` => that many devices;
  - blank `堆叠数量` => 1 device.
- Resulting physical count: 310.

## Example final reporting shape

### By vendor

| 厂商 | 资产条目数 | 折算台数 |
|---|---:|---:|
| Cisco | 171 | 298 |
| Juniper | 12 | 12 |
| 合计 | 183 | 310 |

### By vendor and model — physical count

| 厂商 | 型号 | 折算台数 |
|---|---|---:|
| Cisco | C38XXSwitchStack | 244 |
| Cisco | WS-C3750X | 21 |
| Cisco | CISCO2911 | 8 |
| Cisco | WS-C2960CX-8TC-L | 6 |
| Cisco | C29XXSwitchStack | 5 |
| Cisco | Catalyst 2960-24TT | 4 |
| Cisco | CISCO3845 | 2 |
| Cisco | WS-C3560X-24P | 2 |
| Cisco | WS-C3850-48XS-E | 2 |
| Cisco | WS-C3560G-48TS | 1 |
| Cisco | WS-C3750G-48TS-S | 1 |
| Cisco | WS-C3850-24P | 1 |
| Cisco | cat2960cG8TC | 1 |
| Juniper | EX4300 | 4 |
| Juniper | Juniper-MX5 | 2 |
| Juniper | OvSea-M104 | 2 |
| Juniper | EX2200 | 1 |
| Juniper | EX3400 | 1 |
| Juniper | EX3400.1 | 1 |
| Juniper | M7i | 1 |

## Artifact pattern

Create `/Users/jushuai/My_Project/11/国贸网络设备资产统计_厂商型号.xlsx` with:

- `校验说明`
- `按厂商汇总`
- `按厂商型号汇总`
- `明细`

Then deliver via `MEDIA:/absolute/path`.
