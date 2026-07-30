# Legacy Knowledge Extract — Procurement Receipt Deepen

**Source:** `H:\Workspace\EZAM_CRM - 9.0`（只读）  
**Verified:** 2026-07-23

## Purpose

本包聚焦采购单释放与收货过账的四个边界：

- Draft/Open/Pending 被统一视为 open，导致 Draft 可绕过 Approve 直接 Receive；
- 收货不写 `purchase_receipts`，以 `PO Receipt + PO-{purchase_id}` ledger 作为实际凭证/判重锚；
- Receive 对 inventory、products 镜像、ledger 逐行三写，末尾 PO→Received；
- PO item qty 被一次性全收，无 received/remaining/partial/over-receipt 数量模型。

## Contents

| File | Focus |
|---|---|
| [INDEX.md](INDEX.md) | 主题与风险索引 |
| [po_lifecycle_gates.md](po_lifecycle_gates.md) | Draft/Open/Received 生命周期与 gate |
| [goods_receipt_posting.md](goods_receipt_posting.md) | Goods Receipt 调用、幂等与凭证边界 |
| [receipt_to_stock.md](receipt_to_stock.md) | 收货到库存三写与守恒 |
| [po_qty_control.md](po_qty_control.md) | 订购/已收/未收与超收控制 |

## Authority boundary

- Procurement deepen：[`../procurement-deepen/README.md`](../procurement-deepen/README.md)
- 运行权威：[`../ops/procurement.md`](../ops/procurement.md)

本包仅深化生命周期、过账和数量控制，不重写权威正文。
