# Coding Authorization Summary — PHX-G518 Quote Convert UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Quote Convert UI

## Purpose

Implement the accepted Quote Convert UI over existing governed APIs.

## Scope

Issued Quote Convert confirmation; Conversion detail; Sales Order shell create
from a ready conversion; frontend contracts, browser evidence, and closeout.

## Architecture Boundary

Trusted Tenant/actor context; Conversion Permission default-deny; issued Quote
precondition; idempotent convert; explicit high-impact confirmation; no
Confirm/Issue/Delivery/Invoice/RA expansion.

## In Scope

Only the accepted PHX-G518 UI Gate boundary.

## Out of Scope

Backend, Repository, Database, Alembic, Kernel, Runtime Manifest, Quote Issue
UI, Sales Order Confirm, Delivery, AR Invoice, Return Auth, Finance GL, Brain,
Twin, production, G519+.

## Open Decisions

Existing Convert/Conversion/create-SO endpoints are authoritative; only issued
Quotes convert; idempotent retry returns the existing conversion.

## Risks

Duplicate convert, approval-gate gaps, FX validation, and successor-scope drift.

## Recommendation

**Approved** — implement PHX-G518 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G518**
- Backend/Database/Alembic/Runtime/Production: **None**
- PHX-G519–G525: **None**
