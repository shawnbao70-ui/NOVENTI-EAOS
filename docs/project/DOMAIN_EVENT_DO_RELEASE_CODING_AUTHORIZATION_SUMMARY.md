# Coding Authorization Summary — Domain-event DO.release (G385)

## Milestone

**PHX-G385** — emit `crm.delivery_order.released` on successful `release_delivery_order`.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. After successful release transition (not idempotent replay), enqueue
   `crm.delivery_order.released` via existing `CRMService._emit`.
2. Update commercial catalog + E19 wired set.
3. Contracts asserting single pending outbox entry and no re-emit on retry.

## Out

Catalog + Terminal projection (G386), baseline (G387), Marketplace PSP.

## Product Owner response

**Approve — Batch-A; auto-continue G386–G387.**
