# Decision Summary — CRM Requirement Minimal List Query

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Requirement Minimal List Query

## Purpose

Provide the governed Requirement collection read required to unblock G515.

## Scope

Design tenant-scoped `GET /v1/crm/requirements` with bounded opaque-cursor
pagination and a closed minimal DTO.

## Architecture Boundary

CRM owns the API, Service, and Repository contracts. Trusted ExecutionContext
supplies Tenant authority; Requirement `read` Permission is default-deny.
Kernel and Database schema remain unchanged.

## In Scope

- Active-only Requirement collection
- Default `limit=50`, maximum `100`
- Opaque `updated_at + id` cursor
- Fields: ID, Opportunity ID, code, title, status, updated time, version
- Closed list DTO/envelope
- Tenant, Permission, OpenAPI, pagination, and repository contracts

## Out of Scope

- Writes or lifecycle changes
- Search, import, merge, automation, Quote, or downstream slices
- Database, Alembic, Kernel, Runtime Manifest, frontend, production
- Opening G515 or G516+

## Open Decisions

1. Default limit 50; maximum 100.
2. Archived records are excluded.
3. Cursor ordering is `updated_at + id`.
4. Projection is fixed to approved fields.
5. G515 remains HOLD pending separate Coding Authorization.

## Risks

Tenant-filter drift, unstable ordering, projection expansion, and accidental
milestone resume.

## Recommendation

Approve the minimal query design and retain `Coding Authorization: None`.
