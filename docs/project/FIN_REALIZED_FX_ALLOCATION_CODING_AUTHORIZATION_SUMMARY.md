# Coding Authorization Summary — Realized FX on Allocation (G359)

## Milestone

**PHX-G359** — ADR-0317.5 realized FX shell on cross-currency allocation.

## Alembic

**`0082_finance_realized_fx_allocation_g359`** revising `0081_…`.

## Authorized

1. Allow allocate when receipt.currency != invoice.currency **only if** both
   have FX snapshots; compute functional amounts; record
   `RealizedFxEvent` (or allocation fx_gain_loss fields) = difference in
   functional currency; never silent drop.
2. Same-currency path unchanged (no realized FX row / zero).
3. Optional GL bridge later — this slice may persist event only without
   requiring journal post (document); if easy, post via fx_gain/fx_loss map.
4. HTTP: allocation envelope includes realized_fx_amount / side; contracts.

## Out

Tax void deepen (G360), refund, AP write-off.

## Product Owner response

**Approve — batch; auto-continue G360.**
