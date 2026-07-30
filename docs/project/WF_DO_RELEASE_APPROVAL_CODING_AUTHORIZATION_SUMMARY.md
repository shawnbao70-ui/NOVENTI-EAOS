# Coding Authorization Summary — Workflow Approval DO.release (G365)

## Milestone

**PHX-G365** — ADR-0318; **unique command: DO.release only**.

## Alembic

**`0087_crm_do_release_approval_g365`** revising `0086_…`.

## Authorized

Tenant `do_release_approval_required`; gate `crm.delivery_order.release`;
wire into `release_delivery_order`; approve ≠ auto release; policy routes +
contracts. Mirror G364/G354.

## Out

3WM tolerance (G366), POD, Supplier360.

## Product Owner response

**Approve — batch; auto-continue G366.**
