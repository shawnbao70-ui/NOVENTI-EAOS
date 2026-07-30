# AP 付款深化索引

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`ap_records_lifecycle.md`](ap_records_lifecycle.md) | AP 产生、余额与状态 | `APL-*` |
| [`ap_payment_posting.md`](ap_payment_posting.md) | Treasury 付款与银行镜像 | `APP-*` |
| [`ap_po_gr_link.md`](ap_po_gr_link.md) | AP↔Invoice↔PO↔GR 追溯 | `PGL-*` |
| [`ap_reconcile_absence.md`](ap_reconcile_absence.md) | 分配、核销、三单匹配与对账缺口 | `ARA-*` |

## 交叉引用

- [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)
- [`../finance/receivables-payables.md`](../finance/receivables-payables.md)
- [`../finance/settlement-rules.md`](../finance/settlement-rules.md)

## 总结

1. 运行表是 `ap_records`，不是规格中的 `accounts_payable`。
2. AP 仅随采购发票双写产生，初始且长期为 Unpaid。
3. 发票金额取 PO 头金额；服务端不强制先收货。
4. 收货以 Inventory Ledger 的 `PO Receipt` 代表，`purchase_receipts` 无活动写入。
5. Treasury 付款只写付款流水并扣银行余额。
6. 付款无 `ap_id/invoice_id`，不更新 AP 或采购发票余额。
7. 无 allocation、partial clearing、write-off、vendor statement 或 bank reconciliation。
8. 无 PO/GR/Invoice 三单匹配。
