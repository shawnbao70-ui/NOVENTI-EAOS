# Coding Authorization Summary — PHX-G522 Quote Issue UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Quote Issue UI

## Purpose

Implement the accepted Quote Issue UI over the existing Issue API.

## Scope

Issue action for selected `draft` Quotes; post-issue detail refresh;
frontend contracts, browser evidence, and closeout under PHX-G522 only.

## Architecture Boundary

Trusted Tenant/actor context; Quote `issue` Permission default-deny;
`human_confirm: true`; idempotency; optional approval_ref; no
Convert/Confirm/Delivery/Invoice/RA/Hold expansion. Contiguous after
TRACK-G521; no parallel second milestone.

## In Scope

Only the accepted PHX-G522 UI Gate boundary.

## Out of Scope

Backend beyond existing Issue API, Database, Alembic, Kernel, Runtime
Manifest, Convert behavior changes, Confirm, Delivery, Invoice, RA,
Commercial Hold, production, G523+.

## Open Decisions

Existing Issue endpoint is authoritative; only `draft` Quotes issue;
idempotent retry returns the issued Quote; prerequisite check remains
**no HOLD**.

## Risks

Duplicate Issue, approval-gate gaps, commercial-hold blocks, and
successor-scope drift.

## Recommendation

**Approved** — implement PHX-G522 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G522**
- Backend/Database/Alembic/Runtime/Production: **None**
- PHX-G523–G527: **None**
