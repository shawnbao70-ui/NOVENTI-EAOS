# Coding Authorization Summary — PHX-G525 Return Authorization Read-only UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Return Authorization Read-only UI

## Purpose

Implement the accepted RA create/read UI over existing APIs, using
Delivery-Order-scoped selection (no tenant RA list).

## Scope

Create RA shell from a shipped Delivery Order; RA detail read/refresh;
frontend contracts, browser evidence, and closeout under PHX-G525 only. No
Database/Alembic.

## Architecture Boundary

Trusted Tenant/actor context; `pkg.crm.return_authorization` Permission
default-deny; Create requires `human_confirm: true`, `reason`,
`idempotency_key` (optional `invoice_id`); DO-scoped create+get; no
Restock/Credit Note/Void/Receipt/GL; no Inventory ship UI. Contiguous after
TRACK-G524; no parallel second milestone.

## In Scope

Only the accepted PHX-G525 UI Gate boundary with DO-scoped selection.

## Out of Scope

Tenant RA list; Restock; Credit Note; AR Invoice Void; Receipt; Finance GL;
Inventory ship/unship UI; Database/Alembic/Kernel/Runtime Manifest;
production; G526+.

## Open Decisions

Existing create/get endpoints are authoritative; selection is DO-scoped
create+get (**no HOLD** for list); Create control only when selected DO
status is `shipped`; Restock and Credit Note remain closed; optional
`invoice_id` from selected issued/voided Invoice on same lineage when present.

## Risks

Accidental Restock/Credit Note/Void expansion; create without confirmation;
ship-status confusion; successor-scope drift.

## Recommendation

**Approved** — implement PHX-G525 only (DO-scoped; Create gated on shipped;
no list; no Restock/Credit Note).

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G525**
- Backend/Database/Alembic/Runtime/Production: **None**
- Tenant RA list: **None**
- Inventory ship UI: **None**
- PHX-G526–G527: **None**
