# Decision Summary — CRM Commercial Hold Gate (C11)

> ADR-0321 decision surface; ADR-0315 rewrite boundary applies.

## Package

`pkg.crm` — Commercial hold / confirm gate (minimal)

## Purpose

Add a fail-closed commercial-hold flag on Customer that blocks Sales Order
confirm and Delivery Order create without opening a credit engine.

## Scope

Design boundary only until a separate Coding Authorization assigns PHX-G304.
No credit limit ledger, aging, override, Approval Center, or Finance.

## Architecture Boundary

- Package-owned Customer field and CRM service gate; Kernel untouched
- Tenant isolation via existing CRM repository
- Permission: hold changes use `pkg.crm.customer:update`; confirm/DO keep
  existing resource actions
- Audit: hold set/clear audited; commercial values not required in details

## In Scope

- `customers.commercial_hold` boolean (default false)
- Audited set/clear hold API
- Fail-closed check on SO confirm and DO create via SO→Requirement→Opportunity→Customer
- Missing/incomplete customer lineage fails closed

## Out of Scope

- credit_limit / balance / AR aging engine
- credit override / bypass / exception entity
- Approval Center / Workflow hook (C12)
- PSP, GL, Brain/Twin, Customer360
- Blocking Quote convert or AR Invoice create in this slice

## Open Decisions

- Gate both SO confirm and DO create (not only one): Accept
- Boolean hold only; no numeric limit in C11: Accept
- Hold uses customer `update` permission (no new resource): Accept

## Risks

Low — additive column + two existing write paths; default false preserves
current happy path until an operator sets hold.

## Recommendation

Accept Design Boundary. Architecture approval only; coding authorization
remains `None` until Coding Authorization Summary.

## Product Owner response

**Approve — 2026-07-24 conversation authorization (design only).**
