# PHX-G360 — Tax Red-Credit

System-generated governance implementation artifact; authorization:
[FIN_TAX_VOID_RED_CREDIT_CODING_AUTHORIZATION_SUMMARY.md](FIN_TAX_VOID_RED_CREDIT_CODING_AUTHORIZATION_SUMMARY.md)
and [ADR-0390](../decisions/ADR-0390-finance-tax-red-credit-boundary.md).

- Added Alembic `0083_finance_tax_red_credit_g360`, giving
  `finance.tax_invoices` tenant-scoped original-invoice lineage and an explicit
  `is_red_credit` flag. The unique tenant/original constraint intentionally
  permits one red-credit per original tax invoice.
- `FinanceService.create_tax_red_credit` creates an audited, human-confirmed
  draft credit against only an issued, non-credit original. Amounts are stored
  as positive values; `is_red_credit=True` supplies the credit semantics.
  Omitted amount credits the original amount, while supplied amounts may not
  exceed it. The existing issue command remains the separate issuance step.
- `POST /v1/finance/tax-invoices/{tax_invoice_id}/red-credits` is idempotent
  and exposes the linked original and credit flag. Draft and voided originals
  are rejected. The existing audited void command is unchanged.
- No tax-network behavior, refund, AP write-off, GL posting, Brain, or Twin
  scope was expanded.

Tip verified: `0083_finance_tax_red_credit_g360`
