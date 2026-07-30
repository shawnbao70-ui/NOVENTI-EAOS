# Coding Authorization Summary — PHX-G515 Requirement Managed UI

> Independent Coding Authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Requirement Minimal List Query + Managed UI

## Purpose

Implement the accepted list prerequisite and Requirement UI in one milestone.

## Scope

- `GET /v1/crm/requirements` Repository/Service/API/DTO
- Requirement list/detail/create/edit/archive UI
- Governed Opportunity association
- Contracts, browser evidence, HOLD resolution, closeout

## Architecture Boundary

Trusted Tenant/actor context; server Permission default-deny; stable bounded
cursor; `expected_version`; archive confirmation; no automatic overwrite.

## In Scope

Only implementation required by the two accepted G515 Gates.

## Out of Scope

Database, Alembic, Kernel, Runtime Manifest, Quote/downstream slices, adjacent
packages, production, and G516+.

## Open Decisions

Prerequisite failure keeps G515 HOLD. Default limit 50/max 100; active-only;
`updated_at + id` cursor.

## Risks

Tenant-filter drift, pagination instability, association errors, Permission
projection drift, and concurrency conflicts.

## Recommendation

**Approved** — implement PHX-G515 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G515**
- Database/Alembic: **None**
- Runtime Manifest: **None**
- Production: **None**
- G516–G521: **None**
