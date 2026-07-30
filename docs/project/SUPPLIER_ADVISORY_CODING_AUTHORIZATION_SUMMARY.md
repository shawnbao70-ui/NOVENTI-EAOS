# Coding Authorization Summary — Supplier Advisory / Supplier360 (G391)

## Milestone

**PHX-G391** — expand advisory read source to Supplier360.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. `GET /v1/purchase/suppliers/{id}/advisory` read projection over Supplier360.
2. Closed flags: `read_source=supplier360`, `execution_authority=none`,
   `commercial_auto_write=false`.
3. Reuse Supplier360 permission gate; no Brain/Twin commercial write invent.

## Out

Audit link (G392), baseline (G393), Marketplace PSP.

## Product Owner response

**Approve — Batch-B; auto-continue G392–G393.**
