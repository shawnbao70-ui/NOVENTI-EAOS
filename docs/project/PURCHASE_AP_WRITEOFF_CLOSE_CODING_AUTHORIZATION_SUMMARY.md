# Coding Authorization Summary — AP Write-off + Close (G362)

## Milestone

**PHX-G362** — ADR-0315 supplier-side write-off/close symmetry with G347.

## Alembic

**`0085_purchase_ap_writeoff_close_g362`** revising `0084_…`.

## Authorized

1. `ApWriteOff` against posted/partially_paid ApBill; amount ≤ remaining
   (total − paid_amount − prior write-offs); human_confirm; idempotent.
2. Close bill when remaining == 0 → status `closed` (expand ApBillStatus).
3. Party AP balance subtracts write-offs.
4. HTTP + contracts. Mirror AR patterns.

## Out

Baseline (G363), PSP, Brain silent writes.

## Product Owner response

**Approve — batch; auto-continue G363.**
