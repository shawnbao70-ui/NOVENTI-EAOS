# Finance Knowledge Extract — Index

**Verified:** 2026-07-23 · Source `H:\Workspace\EZAM_CRM - 9.0` (read-only)

| Module | File | Evidence | Primary locus |
|--------|------|----------|---------------|
| 收款 / 应收 | [receipts_ar.md](receipts_ar.md) | Strong (receipts) / Medium (ar_records) | `apps/finance/`, DO invoice path |
| 应收应付综合 | [receivables-payables.md](receivables-payables.md) | Strong for posting; weak for reconciliation closure | `apps/finance/`, `apps/inventory/services.py` |
| 应收与收款勾兑 | [ar_receipt_reconciliation.md](ar_receipt_reconciliation.md) | Strong for SO receipt posting; reconciliation absent | `apps/finance/`, `apps/inventory/services.py` |
| 应付付款与清算 | [ap_payment_clearing.md](ap_payment_clearing.md) | Strong for AP/payment posting; clearing absent | `apps/finance/`, Treasury payment path |
| 发票 | [invoices.md](invoices.md) | Strong for purchase invoices; fragmented for sales invoices | Finance, Inventory, NDE |
| 价格 | [pricing.md](pricing.md) | Strong for quote pricing; weak for price intelligence | Quotation, Product, Finance ops |
| 结算规则 / 佣金 | [settlement-rules.md](settlement-rules.md) | Medium; calculation observable, approval/payout incomplete | Sales commission, TC ledger, Finance boundary |

## Pack rules

Knowledge only; writable under `docs/knowledge/legacy-extract/finance/**`.
