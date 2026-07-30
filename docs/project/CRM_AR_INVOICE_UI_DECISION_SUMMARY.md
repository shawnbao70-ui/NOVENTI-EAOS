# Decision Summary — CRM AR Invoice Read / Issue UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR fifth slice).

## Package

CRM — AR Invoice Read / Issue UI

## Purpose

Provide governed AR Invoice create/read and Issue workflows for released
Delivery Orders.

## Scope

Fifth CRM Business UI serial AK→AR slice; candidate PHX-G524. Invoice read
plus Issue (and create shell from Delivery Order); no Void, Return
Authorization, GL posting, or Receipt UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over existing
`POST /v1/crm/delivery-orders/{id}/ar-invoice`,
`GET /v1/crm/ar-invoices/{id}`, and
`POST /v1/crm/ar-invoices/{id}/issue`. Trusted context supplies Tenant and
actor; server Permission remains authoritative. Issue requires
`human_confirm: true`, idempotency_key, and optional approval_ref. Without a
tenant-scoped Invoice collection, selection is Delivery-Order-scoped
create/get.

## In Scope

- Create AR Invoice shell from a selected released Delivery Order
- Read-only Invoice detail
- Issue with explicit confirmation and post-issue refresh
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Void, Return Authorization, Receipt, Finance GL posting
- Database, Alembic, Kernel, Runtime Manifest unless this slice’s Coding
  Authorization explicitly allows a list prerequisite
- Brain, Twin, production, automatic writes
- G525+

## Open Decisions

1. Existing create/get/issue APIs are the dependencies.
2. No tenant Invoice list; selection is DO-scoped create+get.
3. Only `draft` invoices expose Issue.
4. Idempotent Issue returns the existing issued invoice without overwrite.
5. Missing prerequisite places G524 on HOLD.

## Risks

Missing list, duplicate Issue, accidental Void/GL/Receipt expansion, and
cross-tenant association.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
