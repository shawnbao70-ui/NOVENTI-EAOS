# Coding Authorization Summary — PHX-G517 Quote Lines Managed UI

> Independent authorization under ADR-0321. Approved 2026-07-29.

## Package

CRM — Quote Lines Managed UI

## Purpose

Implement the accepted Quote Lines UI over existing governed APIs.

## Scope

Quote Line list/detail/create/edit/archive UI under the selected Quote Header;
frontend contracts, browser evidence, and milestone closeout.

## Architecture Boundary

Trusted Tenant/actor context; Quote Line Permission default-deny; governed
parent Quote; server-calculated amount; `expected_version`; explicit archive.

## In Scope

Only the accepted PHX-G517 UI Gate boundary.

## Out of Scope

Backend, Repository, Database, Alembic, Kernel, Runtime Manifest, Quote Issue,
Convert, approvals, automatic pricing, adjacent packages, production, G518+.

## Open Decisions

Existing endpoints are authoritative; quantity has three decimals; unit price
has two decimals; conflicts stop and refresh.

## Risks

Decimal projection, parent association, authorization, and concurrency drift.

## Recommendation

**Approved** — implement PHX-G517 only.

## Authorization Record

- Coding Authorization: **Approved**
- Milestone: **PHX-G517**
- Backend/Database/Alembic/Runtime/Production: **None**
- PHX-G518–G521: **None**
