# Coding Authorization Summary — PHX-G514 Opportunity Managed UI

> Phoenix Gate Framework (ADR-0321). **Independent** from Architecture Gate
> Accept. Product Owner approved this slice on 2026-07-28.

## Package

CRM — Opportunity Minimal List Query + Managed UI

## Purpose

Implement the accepted list-query prerequisite and, after it passes, complete
the Opportunity Managed UI in the same serial milestone.

## Scope

One milestone, **PHX-G514**:

- tenant-scoped active Opportunity list query;
- closed minimal API DTO and opaque-cursor pagination;
- Smart Terminal list/detail/create/edit/archive;
- effective-permission-projected controls;
- contract and browser evidence.

## Architecture Boundary

- Existing CRM data model and tables
- Trusted Tenant/actor context only
- Server Permission remains authoritative and default-deny
- Update/archive use `expected_version`
- Archive requires reason and explicit confirmation
- No automatic retry or overwrite

## In Scope

- Repository, Service, Gateway protocol, schema, and router changes required
  only for `GET /v1/crm/opportunities`
- Frontend Opportunity workspace and governed forms
- OpenAPI, tenant, permission, pagination, conflict, UI, and browser contracts
- G514 closeout and HOLD resolution

## Out of Scope

- Database schema, Alembic, Kernel, or Runtime Manifest changes
- Stage automation, scoring, forecasting, search, import, merge, bulk writes
- Requirement, Quote, Sales Order, Customer 360, or adjacent packages
- Production promotion or G515+

## Open Decisions

- Prerequisite failure keeps G514 HOLD and stops.
- Default list limit is 50; maximum is 100.
- Cursor ordering is `updated_at + id`; archived rows are excluded.
- Implementation remains one serial milestone.

## Risks

Tenant-filter drift, unstable pagination, permission-projection mismatch,
concurrency conflicts, and scope expansion remain explicit.

## Recommendation

**Approved** — implement only the accepted G514 scope.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G514**
- Database/Alembic authorization: **None**
- Runtime Manifest authorization: **None**
- Production authorization: **None**
- G515–G521 authorization: **None**
