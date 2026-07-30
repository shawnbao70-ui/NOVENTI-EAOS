# Coding Authorization Summary — Three-Way Match Tolerance (G366)

## Milestone

**PHX-G366** — ADR-0315.5 configurable match tolerance.

## Alembic

**`0088_purchase_3wm_tolerance_g366`** revising `0087_…`.

## Authorized

1. Tenant policy: amount_tolerance (absolute and/or percent), optional qty
   tolerance; default zero = exact match (current behavior).
2. `create_three_way_match` uses policy when comparing PO vs bill.
3. HTTP GET/PUT policy; contracts: within tolerance → matched; outside →
   mismatch.

## Out

POD (G367), Supplier360, baseline.

## Product Owner response

**Approve — batch; auto-continue G367.**
