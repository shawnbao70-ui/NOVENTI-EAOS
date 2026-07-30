# Procurement Receipt Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| PO lifecycle | [po_lifecycle_gates.md](po_lifecycle_gates.md) | 强 | Draft/Open/Pending 同属 open |
| Approve bypass | [po_lifecycle_gates.md](po_lifecycle_gates.md) | 强风险 | Draft 可直接 Receive |
| Goods Receipt | [goods_receipt_posting.md](goods_receipt_posting.md) | 强 | GET 动作，ledger 兼凭证 |
| Receipt idempotency | [goods_receipt_posting.md](goods_receipt_posting.md) | 强/弱 | 应用层 type+remark 判重 |
| Stock posting | [receipt_to_stock.md](receipt_to_stock.md) | 强 | inventory→product→ledger 三写 |
| Qty control | [po_qty_control.md](po_qty_control.md) | 强缺口 | 一次性全收，无 remaining |

## Reading order

1. [po_lifecycle_gates.md](po_lifecycle_gates.md)
2. [goods_receipt_posting.md](goods_receipt_posting.md)
3. [receipt_to_stock.md](receipt_to_stock.md)
4. [po_qty_control.md](po_qty_control.md)

## Shared vocabulary

- **Approve**：Type A `Draft → Open` 人工确认。
- **Receive**：按 PO 全部有效行执行库存三写并置 `Received`。
- **Goods Receipt**：业务收货动作；当前没有独立运行 receipt header/item。
- **PO Receipt ledger**：`trans_type='PO Receipt'`、`remark='PO-{purchase_id}'`。
- **remaining qty**：ordered - cumulative received；Legacy 未建模。
