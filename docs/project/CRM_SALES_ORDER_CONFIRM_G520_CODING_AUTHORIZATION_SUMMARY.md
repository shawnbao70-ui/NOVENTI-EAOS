# Coding Authorization Summary — PHX-G520 Sales Order Confirm UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Sales Order Confirm UI

## Purpose

Implement the accepted Sales Order Confirm UI over the existing Confirm API.

## Scope

Confirm action for selected `created` Sales Orders; post-confirm detail and
line refresh; frontend contracts, browser evidence, and closeout under
PHX-G520 only.

## Architecture Boundary

Trusted Tenant/actor context; Sales Order `confirm` Permission default-deny;
`human_confirm: true`; idempotency; optional approval_ref; no
Delivery/Invoice/RA/Issue expansion. Contiguous after TRACK-G519; no parallel
second milestone.

## In Scope

Only the accepted PHX-G520 UI Gate boundary.

## Out of Scope

Backend beyond existing Confirm API, Database, Alembic, Kernel, Runtime
Manifest, Delivery, Invoice, Return Auth, Quote Issue, production, G521+.

## Open Decisions

Existing Confirm endpoint is authoritative; only `created` orders confirm;
idempotent retry returns the confirmed order; prerequisite check remains
**no HOLD**.

## Risks

Duplicate Confirm, approval-gate gaps, commercial-hold blocks, and
successor-scope drift.

## Recommendation

**Approved** — implement PHX-G520 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G520**
- Backend/Database/Alembic/Runtime/Production: **None**
- PHX-G521–G527: **None**
