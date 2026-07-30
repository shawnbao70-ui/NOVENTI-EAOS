# Decision Summary — CRM Return Authorization Read-only UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR sixth slice).

## Package

CRM — Return Authorization Read-only UI

## Purpose

Provide governed Return Authorization create/read display for a selected
Delivery Order, without Restock or Credit Note writes.

## Scope

Sixth CRM Business UI serial AK→AR slice; candidate PHX-G525. DO-scoped RA
shell create plus read-only detail; no Restock, Credit Note, Invoice Void,
Receipt, or GL UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing
`POST /v1/crm/delivery-orders/{id}/return-authorizations` and
`GET /v1/crm/return-authorizations/{id}`. Trusted context supplies Tenant and
actor; server Permission remains authoritative. Create requires
`human_confirm: true`, `reason`, and `idempotency_key` (optional
`invoice_id`). Without a tenant-scoped RA collection, selection is
Delivery-Order-scoped create/get.

## In Scope

- Create Return Authorization shell from a selected Delivery Order (when API
  lifecycle allows)
- Read-only RA detail and refresh
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Restock, Credit Note, AR Invoice Void, Receipt, Finance GL posting
- Tenant RA list API; Database, Alembic, Kernel, Runtime Manifest unless this
  slice’s Coding Authorization explicitly allows a list prerequisite
- Brain, Twin, production, automatic writes
- G526+

## Open Decisions

1. Existing create/get APIs are the dependencies.
2. No tenant RA list; selection is DO-scoped create+get.
3. “Read-only” excludes Restock and Credit Note; create shell is allowed only
   for selection.
4. Missing prerequisite places G525 on HOLD.
5. Coding Authorization remains independent and default None until separately
   approved.

## Risks

Missing list, accidental Restock/Credit Note/Void expansion, create
confirmation bypass, and cross-tenant association.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
