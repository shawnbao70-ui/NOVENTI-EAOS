# Coding Authorization Summary — PHX-G523 Delivery Order Read / Release UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Delivery Order Read / Release UI

## Purpose

Implement the accepted Delivery Order create/read and Release UI over existing
APIs, using Sales-Order-scoped selection (no tenant DO list).

## Scope

Create DO shell from confirmed Sales Order; DO detail read; Release with
explicit confirmation; frontend contracts, browser evidence, and closeout under
PHX-G523 only. No Database/Alembic.

## Architecture Boundary

Trusted Tenant/actor context; Delivery Order Permission default-deny; Release
`human_confirm: true` + idempotency + optional approval_ref; SO-scoped
create+get (no collection list); no Invoice/RA/ship deepen. Contiguous after
TRACK-G522; no parallel second milestone.

## In Scope

Only the accepted PHX-G523 UI Gate boundary with SO-scoped selection.

## Out of Scope

Tenant DO list/query API, Invoice, RA, inventory ship deepen, Quote Issue
changes, Database/Alembic/Kernel/Runtime Manifest, production, G524+.

## Open Decisions

Existing create/get/release endpoints are authoritative; selection is
SO-scoped create+get (**no HOLD**); only releasable statuses expose Release;
idempotent Release does not overwrite.

## Risks

Duplicate Release, approval-gate gaps, accidental Invoice/Ship expansion, and
successor-scope drift.

## Recommendation

**Approved** — implement PHX-G523 only (SO-scoped; no list prerequisite).

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G523**
- Backend/Database/Alembic/Runtime/Production: **None**
- Tenant DO list: **None**
- PHX-G524–G527: **None**
