# 部分、短收与超收数量模型

**Evidence strength:** Strong-negative for partial/short/over；Strong for full one-shot receive  
**Verified:** 2026-07-23  
**Authority cross-ref:** [`../procurement-receipt-deepen/po_qty_control.md`](../procurement-receipt-deepen/po_qty_control.md)（数量权威；本页深化 partial/short/over 控制缺口）

## Scope 与结论

本页核验 ordered / received / open 数量三元组与 partial / short / over 控制。强结论：Legacy **仅用** `purchase_items.qty` 一次性全收；Receive **不接受**实收数量参数；无 `received_qty` / `open_qty` / `remaining_qty`；无 Partially Received；无短收原因、超收容差、RTV 专用 writer。无效行静默跳过；**不要求**至少一条有效过账行，故全跳过后头状态仍可能 `Received`。

## 数量公式（目标 vs Legacy）

目标模型通常：`remaining = ordered − Σ accepted_received`（± tolerance）。

Legacy 实际：

- `receipt qty = purchase_items.qty`（仅正 qty 行）
- 成功后整 PO → `Received`
- 不保存累计 `Σ received`
- 不保存 rejected / short / over qty
- **无可执行 remaining 公式**

## 业务规则（稳定 ID）

1. **PSO-R01** `purchase_items.qty` 同时充当订购量与收货量。
2. **PSO-R02** 无 `received_qty` / `open_qty` / `remaining_qty` 字段（DDL/服务）。
3. **PSO-R03** `receive_purchase(purchase_id)` 不接受实收数量参数 / 表单。
4. **PSO-R04** 有效正 qty 行一次按原 qty 全量入库。
5. **PSO-R05** 不支持同 PO 多次部分收货（第一次后 status/ledger 阻断）。
6. **PSO-R06** 顺序第二次 Receive → `already_received`（stage 或 ledger）。
7. **PSO-R07** 无 `Partially Received` 头状态或受控转换。
8. **PSO-R08** 无 receipt line 行状态（Accepted / Short / Over）。
9. **PSO-R09** 无短收数量字段与原因码。
10. **PSO-R10** 无超收数量、容差百分比与超差审批。
11. **PSO-R11** 无 accepted / rejected / damaged 数量拆分。
12. **PSO-R12** `qty <= 0` 或无效 `product_id` 行静默 `continue`。
13. **PSO-R13** 循环前只校验「有 items 列表」；不要求至少一条有效过账行。
14. **PSO-R14** 全部行被跳过后仍执行 `update_purchase_status_received`。
15. **PSO-R15** 同 product 多行逐行过账，不预聚合。
16. **PSO-R16** 幂等键为应用层 `trans_type + remark`，不是 DB UNIQUE。
17. **PSO-R17** 无供应商退货 / RTV 专用 writer（采购域）。
18. **PSO-R18** 通用 Inventory Adjust 不能证明 RTV 追溯到 PO 行。
19. **PSO-R19** Invoice 金额来自 PO 头 `total_amount`，不来自实收量汇总。
20. **PSO-R20** NDE / 文档面 `ordered_qty` 类展示词不是收货权威。
21. **PSO-R21** Add item service 不强制 `qty > 0`（可埋下静默 skip 行）。
22. **PSO-R22** 扫码收货复用同一全量 service，无分批 qty UI。

## 流程

1. PO 行保存 `qty`。
2. Receive 读取全部行，不提供实收录入。
3. 正 qty + 有效 product → 三写库存 / 产品 / ledger。
4. 无效行静默跳过。
5. 循环结束后头状态直接 `Received`。
6. 无 remaining → 无法继续部分收货或记录短/超差异。

## 场景矩阵

| 意图 | Legacy 结果 | 缺口 |
|---|---|---|
| 订购 10，一次收 10 | 入库 10，Received | 正常全量 |
| 先收 6 再收 4 | 无实收输入；第二次被拒 | 无 partial |
| 订购 10，实到 8（短收） | 仍按 10 入库或需先改 PO qty | 无 short |
| 订购 10，实到 12（超收） | 无容差/超收录入 | 无 over |
| 行 qty=0 + 有效行 | 0 行 skip；有效行入库；Received | silent skip |
| 全部行 qty≤0 | 可能 0 ledger 仍 Received | silent complete |
| RTV 退回供应商 | 无专用链 | 未建模 |

## 校验（强 / 弱 / 缺失）

1. **PSO-V01（强）** Receive 需 PO open family。
2. **PSO-V02（强）** 需至少一条 purchase item 行记录。
3. **PSO-V03（强）** 需无既有 `PO Receipt` ledger。
4. **PSO-V04（弱）** `qty≤0` 行仅 skip，不报错。
5. **PSO-V05（缺失）** Add item 不强制 `qty>0`。
6. **PSO-V06（缺失）** 无实收 qty 校验 / 上下限。
7. **PSO-V07（缺失）** 无累计 `received ≤ ordered + tolerance`。
8. **PSO-V08（缺失）** 无短收 / 超收原因码。
9. **PSO-V09（缺失）** 无 partial 后保留 open / remaining。
10. **PSO-V10（缺失）** 无 receipt line → PO line 关联。
11. **PSO-V11（缺失）** 无「至少一条有效过账行」校验。
12. **PSO-V12（缺失）** 无 RTV 数量对账。
13. **PSO-V13（缺失）** 无 DB 幂等唯一键。
14. **PSO-V14（缺失）** 无并发收货锁。
15. **PSO-V15（缺失）** 无单位换算 / 包装精度门。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchase_items.qty` | 订购兼一次收货量 |
| `ordered_qty` | NDE/展示词；非收货权威 |
| `received_qty` | **未建模** |
| `open_qty` | **未建模** |
| `remaining_qty` | **未建模** |
| `ledger.qty` | 有效 PO 行过账增量 |
| `balance_qty` | 过账后库存快照 |
| `inventory.stock_qty` | 单一现存量 |
| `products.stock_qty` | 产品库存镜像 |
| `Received` | 整 PO 完成终态 |
| `Partially Received` | **未建模** |
| tolerance | **未建模** |
| rejected_qty / short_qty / over_qty | **未建模** |
| `PO-{id}` | 头级幂等 remark |
| silent skip | 无效行不入库也不报错 |
| silent complete | 零有效过账仍可能完成 |

## 状态词汇

| 词汇 | 判断 |
|---|---|
| Full receipt | **唯一活动模式** |
| Partial / Short / Over | **未建模** |
| Returned to Vendor | **未建模**（无专用 writer） |
| Received | 头级一次性终态 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| PSO-E01 | Receive 只读 PO qty；无实收参数 | 强 | `apps/procurement/services.py`、`repository.py` |
| PSO-E02 | 全量循环 + `qty<=0` silent continue | 强 | `apps/procurement/services.py` |
| PSO-E03 | 循环后无条件 `update_purchase_status_received` | 强 | `apps/procurement/services.py` |
| PSO-E04 | DDL：purchase_items / inventory 无数量三元组 | 强负向 | `runtime/v14/legacy_support.py` |
| PSO-E05 | UI 无实收输入（仅 Receive 链接 + confirm） | 强负向 | `templates/purchase_detail.html`、`purchases.html` |
| PSO-E06 | ledger 判重阻断顺序二次收 | 强 | `apps/procurement/repository.py` |
| PSO-E07 | 扫码复用相同 service | 强 | `apps/inventory/services.py` |
| PSO-E08 | A-004 收货报告（全量 dual-write） | 强 | `docs/reports/Business_Strong_A004_Purchase_Report.md` |
| PSO-E09 | goods-receipt contract 待定义 | 中 | `business_modules/procurement.md` |
| PSO-E10 | 开票取 PO 头总额非实收 | 强 | `apps/finance/services.py` |

## UNKNOWN + 已查路径

1. **线下是否先改 PO qty 再“短收” UNKNOWN。** 已查：PO edit/add item routes、templates、services。
2. **生产零/负 qty 行比例 UNKNOWN。** 已查：静态校验缺口；未查 DB。
3. **供应商实送数量存储位置 UNKNOWN。** 已查：attachments/documents/PO schema。
4. **部分收货外部扩展 / 导入 UNKNOWN。** 已查：integrations 命名面、receipt DDL、imports 命名面。
5. **全 invalid 行完成是否生产发生 UNKNOWN。** 已查：代码路径；未查运行数据。
6. **RTV 是否线下用 Adjust 完成 UNKNOWN。** 已查：Procurement/Inventory Adjust/returns 命名面。
7. **单位换算和包装精度政策 UNKNOWN。** 已查：DDL、templates、business_modules。
8. **并发双收货实际结果 UNKNOWN。** 已查：commit、index、lock 面。
9. **多租户 remark 判重范围 UNKNOWN。** 已查：tenant schema 边界、SQL。
10. **`apps/purchase/` 历史分批收货实现 UNKNOWN。** 已查：目录不存在。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- 已查不存在：`H:\Workspace\EZAM_CRM - 9.0\apps\purchase\`
