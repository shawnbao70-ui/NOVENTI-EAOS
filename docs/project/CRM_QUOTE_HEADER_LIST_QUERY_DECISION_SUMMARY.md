# Decision Summary — CRM Quote Header Minimal List Query

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Quote Header Minimal List Query

## Purpose

Provide the Quote Header collection read required to unblock G516.

## Scope

Design tenant-scoped `GET /v1/crm/quotes` with bounded opaque-cursor pagination
and a closed minimal DTO.

## Architecture Boundary

CRM-owned API/Service/Repository. Trusted ExecutionContext supplies Tenant
authority; Quote `read` Permission is default-deny. No schema or Kernel change.

## In Scope

- Non-archived Quote Header collection
- Default limit 50; maximum 100
- Opaque `updated_at + id` cursor
- Fields: ID, Requirement ID, code, currency, status, updated time, version
- Closed DTO/envelope and tenant/Permission/OpenAPI/pagination contracts

## Out of Scope

- Notes, Quote Lines, Issue, Convert, totals, approvals, writes
- Search, pricing automation, downstream slices
- Database, Alembic, Kernel, Runtime Manifest, frontend, production
- G516 resume or G517+

## Open Decisions

1. Draft and issued Quotes are visible; archived Quotes are excluded.
2. Default limit 50; maximum 100.
3. Cursor order is `updated_at + id`.
4. Projection is fixed to approved fields.
5. G516 stays HOLD pending separate Coding Authorization.

## Risks

Tenant-filter drift, unstable cursors, status/currency projection drift, and
accidental exposure of notes or line data.

## Recommendation

Approve the design and retain `Coding Authorization: None`.
