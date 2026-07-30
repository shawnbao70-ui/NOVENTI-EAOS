# PO 收货控制深化索引

**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

| 文档 | 主题 | 稳定 ID | 核心结论 |
|---|---|---|---|
| [`mandatory_approve_before_receive.md`](mandatory_approve_before_receive.md) | 收货前审批是否强制 | `MAP-*` | 否；Draft 可直接 Receive |
| [`receipt_header_lines.md`](receipt_header_lines.md) | GRN 头行实体与 PO 追溯 | `RHL-*` | 头 DDL 空壳；行缺失；事实在 ledger |
| [`partial_short_over.md`](partial_short_over.md) | 部分、短收、超收数量模型 | `PSO-*` | 仅全量一次收；无三元组/容差 |
| [`quality_disposition_on_receive.md`](quality_disposition_on_receive.md) | 来料质检处置与可用库存 | `QDR-*` | 直接可用入库；无处置链 |

## 交叉引用（邻包权威，不重写）

- [`../procurement-receipt-deepen/po_lifecycle_gates.md`](../procurement-receipt-deepen/po_lifecycle_gates.md) — PO stage / Approve / Receive 门
- [`../procurement-receipt-deepen/goods_receipt_posting.md`](../procurement-receipt-deepen/goods_receipt_posting.md) — GR 过账三写
- [`../procurement-receipt-deepen/po_qty_control.md`](../procurement-receipt-deepen/po_qty_control.md) — qty 模型基础
- [`../procurement-receipt-deepen/receipt_to_stock.md`](../procurement-receipt-deepen/receipt_to_stock.md) — 收货到库存
- [`../quality-compliance/quality_check.md`](../quality-compliance/quality_check.md) — 质检权威（样品/GTFIP/占位）
- [`../quality-compliance/nonconformance.md`](../quality-compliance/nonconformance.md) — 非符合权威

## 总结命题

1. Draft 可直接 Receive；Approve 只负责 Draft→Open（需 human_confirm）。
2. Receive 无 Human Confirm，且为 GET 写动作（`/receive_purchase/{id}`）。
3. `purchase_receipts` 是未使用头表；无 `purchase_receipt_items`。
4. 实际 GR 事实是 `inventory_ledger: trans_type='PO Receipt' + remark='PO-{id}'`。
5. `purchase_items.qty` 同时充当订购量与一次性收货量。
6. 无 received/open/remaining、partial/short/over/tolerance/RTV 专用模型。
7. 无效行可静默跳过；循环后整 PO 仍可能写 Received。
8. 收货直接增加单一可用 `stock_qty`，无质量隔离或 disposition。
