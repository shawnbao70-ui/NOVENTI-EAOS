# Coding Authorization Summary — PHX-G521 Customer 360 Read-only UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Customer 360 Read-only Composition

## Purpose

Implement the accepted Customer 360 read-only Smart Terminal composition over
the existing `/360` API.

## Scope

Selected-Customer 360 panel; commercial_hold and open-order counts; read-only
invoice/receipt/credit traces; frontend contracts, browser evidence, and
closeout under PHX-G521 only.

## Architecture Boundary

Trusted Tenant/actor context; Customer 360 Permission default-deny; read-only
projection; no Commercial Hold write; no Quote Issue / Delivery / Invoice /
Return Authorization. Contiguous after TRACK-G520; no parallel second
milestone.

## In Scope

Only the accepted PHX-G521 UI Gate boundary.

## Out of Scope

Backend beyond existing `/360` API, Database, Alembic, Kernel, Runtime
Manifest, Commercial Hold write, Quote Issue, Delivery, Invoice, Return Auth,
production, G522+.

## Open Decisions

Existing `/360` endpoint is authoritative; no selection means no load; traces
remain non-navigating read-only; prerequisite check remains **no HOLD**.

## Risks

PII/financial-trace creep, accidental Hold/Issue opening, and successor-scope
drift.

## Recommendation

**Approved** — implement PHX-G521 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G521**
- Backend/Database/Alembic/Runtime/Production: **None**
- PHX-G522–G527: **None**
