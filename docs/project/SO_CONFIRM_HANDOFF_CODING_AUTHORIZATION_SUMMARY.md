# Coding Authorization Summary — SO.confirm Handoff #2 (G390)

## Milestone

**PHX-G390** — Brain/Twin commercial handoff #2 targeting SO.confirm only;
authorization ≠ automatic confirm.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. `POST /v1/platform/commercial-handoffs/so-confirm` requiring
   `handoff_so_confirm`, exactly one Brain/Twin source, `human_confirm=true`.
2. Run G335 authorize/execute gate; **do not** call `confirm_sales_order`.
3. Return `auto_confirm=false`, unchanged `sales_order_status`, and
   `approval_ref` for optional later human confirm.
4. No silent Brain commercial writes; Z3 remains `execution_authority=none`.

## Out

Advisory expand (G391), audit link deepen (G392), baseline (G393), other
commercial handoff invent, Marketplace PSP.

## Product Owner response

**Approve — Batch-B; auto-continue G391–G393.**
