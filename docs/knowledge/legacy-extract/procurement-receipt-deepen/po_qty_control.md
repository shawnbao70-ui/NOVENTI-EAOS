# PO Quantity Control：订购、已收、未收与超收

**Evidence strength:** Strong negative for partial/cumulative quantity model  
**结论：** `purchase_items.qty` 同时充当订购量和 Receive 的本次入库量。Receive 没有实收数量输入，按全部正 qty 行一次性入库；系统没有 received_qty、remaining_qty、rejected_qty、over-receipt tolerance 或 receipt item。顺序重收由 PO status/ledger 阻断，但并发、无效行跳过及人工数据不能由数量模型约束。

## 数量公式

目标模型通常需要：

`remaining = ordered - Σ accepted_received`

Legacy 实际是：

- `receipt qty = purchase_items.qty`（对正 qty 行）
- 成功后整个 PO→Received
- 不保存累计 `Σ received`
- 不保存 rejected/short/over qty

因此没有可执行的 remaining 公式。

## 业务规则

| ID | 规则 |
|---|---|
| PQC-R01 | purchase_items.qty 是订购数量。 |
| PQC-R02 | Add item service 不强制 qty>0。 |
| PQC-R03 | Add item service 不强制 cost_price>=0。 |
| PQC-R04 | 行 amount 直接等于 qty×cost_price。 |
| PQC-R05 | Receive 不接受实收 qty 表单。 |
| PQC-R06 | Receive 读取全部 purchase item qty。 |
| PQC-R07 | 正 qty 行按原 qty 全收。 |
| PQC-R08 | 非正 qty 行静默跳过。 |
| PQC-R09 | 一个正行+一个无效行仍可让整个 PO Received。 |
| PQC-R10 | 不存在 received_qty 字段。 |
| PQC-R11 | 不存在 remaining_qty 字段。 |
| PQC-R12 | 不存在 rejected/damaged/quarantine qty。 |
| PQC-R13 | 不存在 receipt line/source purchase item FK。 |
| PQC-R14 | 不支持一次 PO 多次部分收货。 |
| PQC-R15 | 顺序第二次 Receive 由状态/ledger阻断。 |
| PQC-R16 | 同 product 多 PO 行逐行入库，不聚合。 |
| PQC-R17 | 无 over/under receipt 容差或审批。 |
| PQC-R18 | PO Received 不证明每个原始行都有正向 ledger。 |
| PQC-R19 | purchase_receipts 只有 header DDL，仍无 receipt item 数量。 |

## 数量场景

| PO 行 | Receive 结果 | PO 状态 | 缺口 |
|---|---|---|---|
| qty=10 | 入库10 | Received | 正常一次性 |
| 想先收6再收4 | 无实收输入 | — | 不支持 |
| qty=0 | 跳过 | Received（items非空） | 零收货完成 |
| qty=-2 | 跳过 | Received（items非空） | 无效行被掩盖 |
| qty=10，实到12 | 只能系统收10 | Received | 超收2无记录 |
| qty=10，实到8 | 只能系统收10 | Received | 短收2无记录 |
| 两行同产品5+5 | 两次+5 ledger | Received | 无行级 receipt FK |
| 两请求并发 | 均可能通过 precheck | 竞态 | 潜在双收 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| PQC-V01 | Add item PO 必须 open | Hard |
| PQC-V02 | Add item product存在 | Missing |
| PQC-V03 | qty>0 | Missing at add；Receive跳过 |
| PQC-V04 | cost_price>=0 | Missing |
| PQC-V05 | amount 与 qty×cost一致 | 写时计算 |
| PQC-V06 | Receive 有至少一条 item | Hard |
| PQC-V07 | Receive 至少一条有效行 | Missing |
| PQC-V08 | 实收 qty <= remaining | Missing |
| PQC-V09 | 累计 received <= ordered+tolerance | Missing |
| PQC-V10 | 短收/拒收必须记录原因 | Missing |
| PQC-V11 | 部分收货后保留 Open/Partial | Missing |
| PQC-V12 | receipt line 关联 PO line | Missing |
| PQC-V13 | 并发 Receive quantity lock | Missing |
| PQC-V14 | 重复 Receive | Application hard，非 DB unique |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| purchase_items.id | 订购行键，ledger 不引用 |
| purchase_id | 行归属与 receipt remark 来源 |
| product_id | 库存过账产品 |
| qty | 订购量兼一次性收货量 |
| cost_price | 建行成本快照 |
| amount | qty×cost_price |
| PO total_qty | 详情行 qty 求和 |
| PO total_amount | 行 amount 求和镜像 |
| ledger qty | 每个有效行实际写入的正变动 |
| ledger balance | 产品库存过账后余额 |
| Received | PO 头完成标签 |
| received_qty | 未建模 |
| remaining_qty | 未建模 |
| rejected_qty | 未建模 |
| receipt item | 未建模 |
| tolerance | 未建模 |
| partial status | 未建模 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| PQC-E01 | Add item 不校验 qty/cost 正值 | 强负向 | `apps/procurement/services.py::add_purchase_item` |
| PQC-E02 | amount 直接乘法 | 强 | `apps/procurement/services.py` |
| PQC-E03 | Receipt SELECT 只取 product_id/qty | 强 | `apps/procurement/repository.py::fetch_purchase_items_for_receipt` |
| PQC-E04 | Receive 非正 qty 行 continue | 强 | `apps/procurement/services.py::receive_purchase` |
| PQC-E05 | Receive 无实收 qty 参数 | 强负向 | `apps/procurement/router.py`、`services.py` |
| PQC-E06 | PO/line DDL 无 received/remaining | 强负向 | `runtime/v14/legacy_support.py` |
| PQC-E07 | purchase_receipts DDL 无 receipt items | 强负向 | `runtime/v14/legacy_support.py` |
| PQC-E08 | 成功后整个 PO Received | 强 | `apps/procurement/repository.py::update_purchase_status_received` |
| PQC-E09 | UI 无 partial receipt input | 强负向 | `templates/purchase_detail.html`、`purchases.html` |
| PQC-E10 | Procurement 权威确认一次性全收 | 强交叉 | `../ops/procurement.md` |

## UNKNOWN + 已查路径

1. **短收/超收是否线下修改 PO qty 后再收 UNKNOWN。** 已查：PO edit routes/templates/services；未见 qty edit。
2. **生产数据中零/负 qty 行规模 UNKNOWN。** 已查静态校验；未读生产 DB。
3. **supplier delivery note 是否保存实收数量 UNKNOWN。** 已查：documents/attachments/Procurement。
4. **purchase_receipts 是否有私有 receipt item 扩展 UNKNOWN。** 已查：公开 DDL/migrations/apps。
5. **并发 Receive 双收是否生产复现 UNKNOWN。** 已查：precheck/transaction/DB config。
6. **质检接受量与入库量应如何区分 UNKNOWN。** 已查：Quality/Procurement/Inventory modules。
7. **单位换算、包装单位和小数精度规则 UNKNOWN。** 已查：schemas/templates/business_modules。
8. **PO invoice qty 是否应与 receipt qty 三单匹配 UNKNOWN。** 已查：Finance purchase invoice、AP、Procurement reports。

## 交叉引用

- Procurement deepen：[`../procurement-deepen/README.md`](../procurement-deepen/README.md)
- 运行权威：[`../ops/procurement.md`](../ops/procurement.md)
