# Coding Authorization Summary — PHX-G512 CRM List Query Prerequisite

> Phoenix Gate Framework (ADR-0321). **Independent** from Architecture Gate
> Accept. Product Owner approved this implementation slice in conversation on
> 2026-07-28.

## Package

`noventi.crm` — Customer + Contact Minimal List Query

## Purpose

Implement the Gate-Accepted collection-query prerequisite that blocks the
PHX-G512 read-only CRM UI.

## Scope

Extend the same serial milestone **PHX-G512**. No second milestone is opened.

## Architecture Boundary

- Changes are limited to CRM service, Repository, Gateway, DTO/OpenAPI, tests,
  and the already-authorized frontend after prerequisite verification.
- Tenant authority comes from trusted ExecutionContext.
- Customer/Contact `read` Permission remains default-deny.
- Kernel and Database schema remain unchanged.
- Contact collection responses exclude email and phone.

## In Scope

- `GET /v1/crm/customers`
- `GET /v1/crm/customers/{customer_id}/contacts`
- Default `limit=50`, maximum `100`
- Opaque cursor and stable ordering
- Active-only default
- Existing in-memory and persistent Repository implementations
- Tenant, Permission, PII, OpenAPI, and contract tests
- Resume the already-authorized read-only CRM UI after prerequisite evidence

## Out of Scope

- Business writes
- Database or Alembic changes
- Search, import, merge, or Customer 360
- Runtime Manifest changes
- Contact email/phone collection fields
- A second milestone or production promotion

## Open Decisions

- Authorized milestone: **PHX-G512**
- Repository inability to provide migration-free stable pagination produces
  Hold.
- Passing prerequisite tests resolves only this Hold and does not widen UI
  scope.
- Baseline failures may not be bypassed.

## Risks

- Cursor boundaries can duplicate or omit records.
- Repository ordering can drift.
- Incorrect tenant or Permission filters can expose data.
- API completion can be mistaken for production GO.

## Recommendation

**Approved** — implement the PHX-G512 list-query prerequisite, then continue
the existing read-only CRM UI authorization without opening another milestone.

## Prerequisites

- Gate Acceptance:
  [CRM_CUSTOMER_CONTACT_LIST_QUERY_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_LIST_QUERY_ACCEPTANCE.md)
- Existing UI HOLD:
  [CRM_CUSTOMER_CONTACT_UI_G512_HOLD.md](CRM_CUSTOMER_CONTACT_UI_G512_HOLD.md)
- Product Owner decision: **Approve — 2026-07-28**
- Milestone: **PHX-G512**

## Authorization Record

- Coding Authorization: **Approved**
- Authorized milestone: **PHX-G512**
- Database/Alembic authorization: **None**
- Runtime Manifest authorization: **None**
- Production authorization: **None**
