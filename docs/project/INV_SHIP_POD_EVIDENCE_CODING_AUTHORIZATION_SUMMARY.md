# Coding Authorization Summary — Ship POD / Evidence Shell (G367)

## Milestone

**PHX-G367** — ADR-0314.7 ship evidence linked to ship identity.

## Alembic

**`0089_inventory_ship_pod_g367`** revising `0088_…`.

## Authorized

1. Persist POD/evidence on ship posting: optional `pod_ref`, `pod_captured_at`,
   or evidence rows keyed by ship posting id.
2. Tenant policy `ship_pod_required` (default false): when true, ship requires
   pod_ref (or evidence); when false, ship unchanged.
3. HTTP: ship request accepts pod fields; GET ship/DO exposes evidence.
4. Contracts. Complete ≠ bare confirm without policy.

## Out

Supplier360 (G368), baseline, carrier network live.

## Product Owner response

**Approve — batch; auto-continue G368.**
