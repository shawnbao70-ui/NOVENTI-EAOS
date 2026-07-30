# Coding Authorization Summary — AR Write-off + Close (G347)

## Milestone

**PHX-G347** — ADR-0315.2 write-off / close shell.

## Alembic

**`0072_finance_ar_writeoff_close_g347`** revising
`0071_finance_tax_credit_link_g344`.

## Authorized

1. AR write-off entity/command against issued invoice (amount ≤ remaining =
   invoice total − allocations − prior write-offs); human_confirm; idempotent.
2. Invoice close when remaining == 0 (fully allocated and/or written off);
   status expand: add `closed` (and track write_off_amount on invoice or
   separate write_off rows).
3. Party balance (G346) must subtract write-offs.
4. HTTP + contracts. No auto write-off from Brain; no refund payout.

## Out

Workflow (G348), fulfillment, FX cash, Cap widen.

## Product Owner response

**Approve — batch; auto-continue G348 (Quote.issue).**
