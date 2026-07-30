# Decision Summary — CRM Opportunity Minimal List Query

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated artifacts are not Product
> Owner editing surfaces.

## Package

CRM — Opportunity Minimal List Query

## Purpose

Provide the governed Opportunity collection read required to unblock the
candidate PHX-G514 Opportunity Managed UI.

## Scope

Design a tenant-scoped `GET /v1/crm/opportunities` collection contract with
bounded opaque-cursor pagination and a minimal closed response DTO.

## Architecture Boundary

The query remains CRM Package-owned. Tenant authority comes only from trusted
ExecutionContext, Opportunity `read` Permission remains default-deny, and the
client cannot override tenant context. Kernel and Database schema remain
unchanged.

## In Scope

- Tenant-scoped service and Repository collection query
- `GET /v1/crm/opportunities`
- Closed paginated response envelope
- Default `limit=50`, maximum `limit=100`
- Opaque cursor with stable `updated_at + id` ordering
- Active-only default result set
- List fields: ID, Customer ID, code, title, status, owner subject ID, updated
  time, and version
- Tenant, Permission, OpenAPI, pagination, and contract evidence

## Out of Scope

- Opportunity writes or lifecycle changes
- Database schema or Alembic changes
- Search, forecasting, scoring, stage automation, import, merge, or bulk work
- Requirement, Quote, Sales Order, Customer 360, or adjacent packages
- Runtime Manifest, frontend implementation, production promotion
- Opening G514 or successor milestones

## Open Decisions

1. Default `limit=50`; maximum `limit=100`.
2. Cursor is opaque and ordered by `updated_at + id`.
3. Archived records are excluded by default.
4. Collection fields are fixed to the approved minimal projection.
5. G514 remains HOLD until a separate Coding Authorization implements and
   verifies this prerequisite.

## Risks

- Pagination can leak cross-tenant records if repository filtering drifts.
- Unstable ordering can skip or duplicate records.
- Owner identifiers can widen collection exposure.
- Gate acceptance can be mistaken for automatic G514 resume.

## Recommendation

Approve the minimal Opportunity collection-query design. Keep
`Coding Authorization: None` and G514 on HOLD pending separate authorization.
