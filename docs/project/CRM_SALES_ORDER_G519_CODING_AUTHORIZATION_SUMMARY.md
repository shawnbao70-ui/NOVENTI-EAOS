# Coding Authorization Summary — PHX-G519 Sales Order Read-only UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Sales Order Minimal List Query + Read-only UI

## Purpose

Implement the accepted list prerequisite, resolve HOLD, and deliver Sales Order
read-only Smart Terminal UI.

## Scope

`GET /v1/crm/sales-orders` Repository/Service/API/DTO; list/detail/line read UI;
contracts, browser evidence, and closeout.

## Architecture Boundary

Trusted Tenant/actor context; Sales Order Permission default-deny; bounded
`created_at + id` cursor; read-only controls; no Confirm/Delivery/Invoice/RA.

## In Scope

Only the two accepted G519 Gate boundaries.

## Out of Scope

Confirm, Delivery, Invoice, Return Auth, Database, Alembic, Kernel, Runtime
Manifest, adjacent packages, production, G520+.

## Open Decisions

All existing statuses visible; default limit 50/max 100; cursor on
`created_at + id`; prerequisite failure retains HOLD.

## Risks

Tenant, cursor, status/total projection, and accidental Confirm-scope drift.

## Recommendation

**Approved** — implement PHX-G519 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G519**
- Database/Alembic/Runtime/Production: **None**
- PHX-G520–G525: **None**
