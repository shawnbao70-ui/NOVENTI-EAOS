# PHX-G362 — AP Write-off + Close

System-generated governance implementation artifact; authorization:
[PURCHASE_AP_WRITEOFF_CLOSE_CODING_AUTHORIZATION_SUMMARY.md](PURCHASE_AP_WRITEOFF_CLOSE_CODING_AUTHORIZATION_SUMMARY.md)
and [ADR-0392](../decisions/ADR-0392-purchase-ap-writeoff-close-boundary.md).

- Added Alembic `0085_purchase_ap_writeoff_close_g362`, creating tenant-scoped
  `purchase.ap_write_offs`, adding `ap_bills.write_off_amount`, and extending
  the AP bill lifecycle with `closed`.
- `PurchaseService.create_ap_write_off` is permissioned, audited,
  human-confirmed, idempotent, and bounded by the outstanding bill amount.
  `close_ap_bill` is separately human-confirmed and succeeds only when the
  paid plus written-off amount settles the bill.
- `POST /v1/purchase/ap-write-offs` and
  `POST /v1/purchase/ap-bills/{id}/close` expose the workflow. Supplier AP
  balances now subtract applied write-offs; no PSP, GL posting, or external
  payment execution is introduced.

Tip verified: `0085_purchase_ap_writeoff_close_g362`
