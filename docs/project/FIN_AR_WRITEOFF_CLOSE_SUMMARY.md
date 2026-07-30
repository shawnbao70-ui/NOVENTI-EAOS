# PHX-G347 Summary — AR Write-off + Close

**Status:** COMPLETE  
**Alembic tip:** `0072_finance_ar_writeoff_close_g347`

## Delivered

- Finance-owned, tenant-scoped AR write-off rows with idempotency, human
  confirmation, Permission, and audit evidence.
- Remaining exposure is `invoice total − receipt allocations − write-offs`;
  over-write-off is rejected.
- `POST /v1/finance/ar-invoices/{invoice_id}/close` closes only a zero-remaining
  issued invoice through the Finance-to-CRM close port.
- Party Balance Authority subtracts write-offs from issued AR exposure.

## Boundary confirmation

No automatic Brain write-off, refunds, payouts, FX cash flow, or GL posting was
introduced. AR invoice status remains CRM-owned; Finance invokes only the
dedicated close port after validating financial remaining amount.

## Evidence

- Coding authorization:
  `docs/project/FIN_AR_WRITEOFF_CLOSE_CODING_AUTHORIZATION_SUMMARY.md`
- Boundary: `docs/decisions/ADR-0379-finance-ar-writeoff-close-boundary.md`
- Contract test:
  `tests/contracts/test_api_gateway_g347_finance_ar_writeoff_close.py`
