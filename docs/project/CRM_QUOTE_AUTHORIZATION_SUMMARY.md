# Decision Summary — CRM Quote (C4)

> Phoenix Gate Framework: ADR-0321. Product Owner decision surface only.

## Package

`noventi.crm` — Quote minimal draft shell (C4)

## Purpose

Define the first tenant-safe Quote record below an existing Requirement,
without opening pricing, lines, issuance, approval, conversion, orders or
finance.

## Architecture Boundary

- Quote belongs to `noventi.crm` for this CRM vertical slice.
- Every Quote must reference one active same-tenant Requirement.
- IDs are opaque and code is system-assigned.
- Permission is default-deny; writes are audited without commercial notes.

## In Scope

- Opaque ID, system code, mandatory Requirement
- ISO-style three-letter currency label (default `USD`) and optional notes
- `draft` / `archived` lifecycle with optimistic versioning
- Resource `pkg.crm.quote`; create/read/update/archive

## Out of Scope

- Quote lines, product/catalog lookup, quantities, prices, totals, tax,
  discount, FX execution, margin or pricing engine
- Send/issue/approve/negotiate/win/loss and Approval Center
- Convert, Sales Order, Finance, PSP, print/PDF/templates/version history
- Sample, AI, Brain/Twin, runtime events, Legacy code/SQL/roles

## Open Decisions

- Requirement is mandatory and immutable: Accept proposed.
- C4 is a draft shell; no price or line claims: Accept proposed.
- Lifecycle is only `draft` / `archived`: Accept proposed.
- Currency is a validated label, not an FX calculation: Accept proposed.

## Recommendation

Accept Design Boundary for C4 only.

## Product Owner response

**Approve — 2026-07-24 (conversation preauthorization; design boundary only).**
