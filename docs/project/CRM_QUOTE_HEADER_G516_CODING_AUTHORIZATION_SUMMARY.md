# Coding Authorization Summary — PHX-G516 Quote Header Managed UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Quote Header Minimal List Query + Managed UI

## Purpose

Implement the accepted list prerequisite and Quote Header UI.

## Scope

`GET /v1/crm/quotes` Repository/Service/API/DTO; list/detail/create/edit/archive
UI; governed Requirement association; contracts, browser evidence, closeout.

## Architecture Boundary

Trusted Tenant/actor context; Quote Permission default-deny; bounded cursor;
`expected_version`; archive confirmation; no automatic overwrite.

## In Scope

Only the two accepted G516 Gate boundaries.

## Out of Scope

Quote Lines, Issue, Convert, approvals, Database, Alembic, Kernel, Runtime
Manifest, adjacent packages, production, G517+.

## Open Decisions

Draft/issued list; archived excluded; default limit 50/max 100; prerequisite
failure retains HOLD.

## Risks

Tenant, cursor, currency/status projection, association, and concurrency drift.

## Recommendation

**Approved** — implement PHX-G516 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G516**
- Database/Alembic/Runtime/Production: **None**
- PHX-G517–G521: **None**
