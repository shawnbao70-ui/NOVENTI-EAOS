# PHX-G361 — AR Refund ↔ Credit Note

System-generated governance implementation artifact; authorization:
[FIN_AR_REFUND_CODING_AUTHORIZATION_SUMMARY.md](FIN_AR_REFUND_CODING_AUTHORIZATION_SUMMARY.md)
and [ADR-0391](../decisions/ADR-0391-finance-ar-refund-boundary.md).

- Added Alembic `0084_finance_ar_refund_g361`, creating tenant-scoped
  `finance.ar_refunds` with Credit Note and customer lineage, idempotency, and
  the `draft|posted` lifecycle.
- `FinanceService.create_ar_refund` requires an issued Credit Note, derives
  customer and currency from it, and rejects amounts exceeding its amount or a
  currency mismatch. `post_ar_refund` is separately permissioned, audited, and
  requires explicit human confirmation.
- `POST /v1/finance/ar-refunds` and
  `POST /v1/finance/ar-refunds/{refund_id}/post` expose the registration and
  posting workflow. They register refund intent only; no PSP payout, bank
  transfer, or payment execution is present.

Tip verified: `0084_finance_ar_refund_g361`
