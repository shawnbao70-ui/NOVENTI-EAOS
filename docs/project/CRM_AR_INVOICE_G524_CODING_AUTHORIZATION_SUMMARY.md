# Coding Authorization Summary — PHX-G524 AR Invoice Read / Issue UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — AR Invoice Read / Issue UI

## Purpose

Implement the accepted AR Invoice create/read and Issue UI over existing APIs,
using Delivery-Order-scoped selection (no tenant Invoice list).

## Scope

Create Invoice shell from released Delivery Order; Invoice detail read; Issue
with explicit confirmation; frontend contracts, browser evidence, and closeout
under PHX-G524 only. No Database/Alembic.

## Architecture Boundary

Trusted Tenant/actor context; AR Invoice Permission default-deny; Issue
`human_confirm: true` + idempotency + optional approval_ref; DO-scoped
create+get (no collection list); no Void/RA/Receipt/GL posting. Contiguous
after TRACK-G523; no parallel second milestone.

## In Scope

Only the accepted PHX-G524 UI Gate boundary with DO-scoped selection.

## Out of Scope

Tenant Invoice list/query API, Void, RA, Receipt, Finance GL posting,
Database/Alembic/Kernel/Runtime Manifest, production, G525+.

## Open Decisions

Existing create/get/issue endpoints are authoritative; selection is DO-scoped
create+get (**no HOLD**); only `draft` invoices expose Issue; idempotent Issue
does not overwrite.

## Risks

Duplicate Issue, approval-gate gaps, accidental Void/GL/Receipt expansion, and
successor-scope drift.

## Recommendation

**Approved** — implement PHX-G524 only (DO-scoped; no list prerequisite).

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G524**
- Backend/Database/Alembic/Runtime/Production: **None**
- Tenant Invoice list: **None**
- PHX-G525–G527: **None**
