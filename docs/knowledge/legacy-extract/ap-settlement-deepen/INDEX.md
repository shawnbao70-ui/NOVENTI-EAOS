# AP Settlement Deepen — Index

| Topic | Primary page | Evidence strength | Key conclusion |
|---|---|---|---|
| PO→Invoice | [invoice_po_gr_match.md](invoice_po_gr_match.md) | 强 | 一 PO 应用层最多一 Invoice |
| GR match | [invoice_po_gr_match.md](invoice_po_gr_match.md) | 强缺口 | ledger 软链接，不参与 Invoice gate |
| Payment allocation | [payment_allocation.md](payment_allocation.md) | 强缺口 | Payment 无 AP/Invoice FK |
| Partial clearing | [partial_clearing_writeoff.md](partial_clearing_writeoff.md) | 强缺口 | paid/balance/status 不推进 |
| Write-off/reversal | [partial_clearing_writeoff.md](partial_clearing_writeoff.md) | 强缺口 | 无一等实体/命令 |
| Supplier balance | [supplier_balance_authority.md](supplier_balance_authority.md) | 混合 | AP 与付款两套事实未对账 |

## Reading order

1. [invoice_po_gr_match.md](invoice_po_gr_match.md)
2. [payment_allocation.md](payment_allocation.md)
3. [partial_clearing_writeoff.md](partial_clearing_writeoff.md)
4. [supplier_balance_authority.md](supplier_balance_authority.md)

## Shared vocabulary

- **三单匹配**：PO、Goods Receipt、Supplier Invoice 的数量/金额/来源一致性。
- **Allocation**：将一笔 payment 的金额分配到一条或多条 AP/Invoice。
- **Clearing**：依据 allocation 更新 paid、balance、status。
- **Write-off**：经授权将小额/无法支付余额核销。
- **Supplier balance authority**：可唯一解释供应商净未付责任的主账。
