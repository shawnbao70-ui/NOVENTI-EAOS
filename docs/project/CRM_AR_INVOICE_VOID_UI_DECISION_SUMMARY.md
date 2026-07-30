# Decision Summary — CRM AR Invoice Void UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR seventh slice).

## Package

CRM — AR Invoice Void UI

## Purpose

Provide governed Void for a selected issued AR Invoice with explicit
confirmation.

## Scope

Seventh CRM Business UI serial AK→AR slice; candidate PHX-G526. Void on
selected issued Invoice only; no Receipt, GL posting, RA Restock/Credit Note,
or Commercial Hold UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing
`POST /v1/crm/ar-invoices/{id}/void`. Trusted context supplies Tenant and
actor; server Permission (`void` on `pkg.crm.ar_invoice`) remains
authoritative. Void requires `human_confirm: true`, `reason`, and
`idempotency_key`. Selection continues from the governed G524 Invoice surface
(no tenant Invoice list).

## In Scope

- Void control when selected Invoice status is `issued` and permission allows
- Explicit confirmation, reason, and post-void refresh
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Receipt, Finance GL posting, RA Restock/Credit Note, Commercial Hold
- Tenant Invoice list; Database, Alembic, Kernel, Runtime Manifest unless this
  slice’s Coding Authorization explicitly allows a list prerequisite
- Brain, Twin, production, automatic writes
- G527+

## Open Decisions

1. Existing void API is the dependency.
2. Only `issued` invoices expose Void; idempotent void of already-voided
   returns existing without overwrite.
3. No tenant Invoice list; selection remains DO-scoped create/get from G524.
4. Missing prerequisite places G526 on HOLD.
5. Coding Authorization remains independent and default None until separately
   approved.

## Risks

Accidental GL/Receipt/Hold expansion, void without confirmation, and
cross-tenant association.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
