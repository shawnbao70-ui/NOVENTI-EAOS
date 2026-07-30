# Coding Authorization Summary — Controlled Unship (G355)

## Milestone

**PHX-G355** — ADR-0314.6 controlled Unship (≠ Reopen / ≠ RMA).

## Alembic

**`0079_inventory_controlled_unship_g355`** revising
`0078_inventory_do_ship_approval_g354`.

## Authorized

1. Explicit `unship_delivery_order` command: reverse ship posting for a
   **shipped** DO; restore inventory on_hand; reduce SO shipped_quantity /
   reopen remaining qty; DO returns to released (or unshipped) state with new
   identity/audit — not silent status flip.
2. human_confirm + Permission; idempotent unship_key; fail-closed if already
   unshipped / never shipped / RMA linked if that blocks.
3. Does NOT implement Reopen-as-unship; does NOT create RMA/credit note.
4. HTTP + contracts; ship idempotency preserved.

## Out

Commission (G356), baseline (G357), carrier/POD, Brain silent writes.

## Product Owner response

**Approve — batch; auto-continue G356.**
