# Coding Authorization Summary — Workflow Approval DO.ship (G354)

## Milestone

**PHX-G354** — ADR-0318; **unique command: DO.ship only**.

## Alembic

**`0078_crm_do_ship_approval_g354`** revising G353 tip (or none).

## Authorized

Tenant `do_ship_approval_required`; gate action `inventory.delivery_order.ship`
(or `crm.delivery_order.ship`); `ship_delivery_order` blocked until approved;
approve ≠ auto ship; policy off = unchanged.

## Out

Unship (G355), commission, Cap widen.

## Product Owner response

**Approve — batch; auto-continue G355.**
