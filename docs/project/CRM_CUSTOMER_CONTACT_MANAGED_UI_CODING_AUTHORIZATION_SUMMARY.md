# Coding Authorization Summary — CRM C18 Managed UI

> Phoenix Gate Framework (ADR-0321). **Independent** from Architecture Gate
> Accept. Product Owner approved this slice on 2026-07-28.

## Package

`noventi.crm` — C18 Customer + Contact Managed UI

## Purpose

Implement the Gate-Accepted Customer/Contact create, edit, and archive UI.

## Scope

One serial milestone, **PHX-G513**. Changes are limited to Smart Terminal
frontend, frontend contracts/tests, and milestone evidence.

## Architecture Boundary

- Existing CRM APIs only
- Existing effective-permissions query controls write affordance visibility
- Permission uncertainty fails closed
- Tenant is never placed in request bodies
- Update/archive use `expected_version`
- Archive requires reason and secondary confirmation

## In Scope

- Customer and Contact create/edit/archive
- Form validation and optional Contact PII
- 403/404/409/422 handling
- Conflict refresh without automatic overwrite
- Post-success list/detail refresh
- UI/API regression and browser verification
- PHX-G513 closeout evidence

## Out of Scope

- API, Service, Repository, Database, or Alembic changes
- Hard delete, merge, import, deduplication, commercial hold, Customer 360
- Runtime Manifest, bulk/automatic writes, production promotion
- A second parallel milestone

## Open Decisions

- Milestone: **PHX-G513**
- Missing/ambiguous effective permissions hide all write controls.
- 409 never retries or overwrites automatically.
- Browser verification uses isolated test data only.
- Baseline failure produces Hold.

## Risks

Permission-projection drift, PII exposure, concurrency conflict, and
production-status confusion remain explicit.

## Recommendation

**Approved** — implement only CRM C18 Managed UI under PHX-G513.

## Prerequisites

- Gate Acceptance:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_ACCEPTANCE.md)
- Prior read-only UI:
  [CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md)
- Product Owner decision: **Approve — 2026-07-28**
- Milestone: **PHX-G513**

## Authorization Record

- Coding Authorization: **Approved**
- Backend/Database/Alembic authorization: **None**
- Runtime Manifest authorization: **None**
- Production authorization: **None**
