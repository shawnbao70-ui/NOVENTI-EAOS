# Coding Authorization Summary — CRM C17 Customer + Contact Read-only UI Shell

> Phoenix Gate Framework (ADR-0321). **Independent** from Architecture Gate
> Accept. Product Owner approved this implementation slice in conversation on
> 2026-07-28.

## Package

`noventi.crm` — C17 Customer + Contact Read-only UI Shell

## Purpose

Authorize implementation of the Gate-Accepted CRM Customer and Contact
read-only business UI.

## Scope

One serial milestone, **PHX-G512**. Authorization is limited to existing
frontend surfaces, frontend tests, required governance evidence, and milestone
closeout.

## Architecture Boundary

- UI remains inside the CRM Business Package.
- Existing governed query interfaces may be reused but not expanded.
- Tenant authority comes from trusted execution context.
- Server-side Permission evaluation remains the authorization truth.
- Interface insufficiency fails closed and requires a separate Gate.

## In Scope

- CRM navigation and routing
- Customer list and detail presentation
- Contact list and detail presentation
- Loading, empty, denied, and error states
- Hidden or non-actionable unauthorized operations
- UI unit/component tests and required documentation
- PHX-G512 acceptance and closeout evidence

## Out of Scope

- New or modified API, CRUD, Repository, Database, or Alembic behavior
- Customer or Contact business writes
- Runtime Manifest changes
- Import, merge, Customer 360, Finance, Workflow, Brain, or Twin
- Production promotion
- A second parallel milestone

## Open Decisions

- Milestone: **PHX-G512**
- Existing interface gaps stop this slice; they do not authorize backend work.
- Write operations must not appear actionable.
- Baseline failure produces Hold; tests may not be bypassed.

## Risks

- Existing interfaces may omit desired presentation data.
- Frontend permission presentation could be mistaken for a security boundary.
- UI completion could be mistaken for production GO.

## Recommendation

**Approved** — implement only CRM C17 Customer + Contact Read-only UI Shell
under PHX-G512. Do not open another milestone before G512 completion.

## Prerequisites

- Gate Acceptance:
  [CRM_CUSTOMER_CONTACT_UI_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_UI_ACCEPTANCE.md)
- Architecture Gate:
  [CRM_CUSTOMER_CONTACT_UI_ARCHITECTURE_GATE.md](CRM_CUSTOMER_CONTACT_UI_ARCHITECTURE_GATE.md)
- Product Owner decision: **Approve — 2026-07-28**
- Milestone: **PHX-G512**

## Authorization Record

- Coding Authorization: **Approved**
- Authorized milestone: **PHX-G512**
- Production authorization: **None**
- Runtime Manifest authorization: **None**
- Backend expansion authorization: **None**
