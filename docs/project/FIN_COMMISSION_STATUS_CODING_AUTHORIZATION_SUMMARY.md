# Coding Authorization Summary — Commission Status Deepen (G356)

## Milestone

**PHX-G356** — commission accrued→payable→paid (observable failures).

## Alembic

**`0080_finance_commission_status_g356`** revising
`0079_inventory_controlled_unship_g355` (expand status check).

## Authorized

1. Expand `CommissionStatus`: `accrued|payable|paid` (optional `cancelled` if
   clean); transitions via explicit commands with human_confirm where
   high-impact; fail-closed illegal jumps; audit each transition.
2. HTTP mark-payable / mark-paid (or single transition endpoint); GET shows
   status; GL bridge still requires accrued or document if payable allowed.
3. Contracts: happy path + illegal transition 409; no silent auto from Convert.

## Out

Baseline (G357), Cap widen, Brain silent writes, payout PSP.

## Product Owner response

**Approve — batch; auto-continue G357.**
