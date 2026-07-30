# Decision Summary — CRM Requirement (C3)

> Phoenix Gate Framework: ADR-0321. Product Owner decision surface only.

## Package

`noventi.crm` — Requirement minimal vertical slice (C3)

## Purpose

Define a tenant-safe business Requirement immediately below an existing
Opportunity, without opening Analysis, Sample, Quote, Convert, or AI matching.

## Scope

Design boundary only. Customer, Contact, and Opportunity remain the previously
accepted CRM capabilities. Kernel remains unchanged.

## Architecture Boundary

- Requirement belongs to `noventi.crm`, not Kernel.
- Every Requirement must reference an existing active Opportunity in the same
  trusted tenant.
- IDs are package-owned and opaque; code is system-assigned.
- Permission is default-deny; no owner field is introduced in C3.
- Writes must be auditable; no runtime event schema is accepted.

## In Scope

- Opaque ID, system code, required title and optional description
- `active` / `archived` lifecycle with optimistic versioning
- Resource type `pkg.crm.requirement`
- Permissioned create/read/update/archive and persistence tests

## Out of Scope

- Product analysis/matching, Sample, Quote, Convert, Sales Order, Finance
- Requirement360, downstream trace links, cached requirement counts
- Legacy lifecycle tokens, AI analysis fields, mining/insight auto-write
- Brain/Twin, runtime events, hard delete, import/merge/search

## Open Decisions

- Opportunity association is mandatory and immutable in C3: Accept proposed.
- Lifecycle remains `active` / `archived`: Accept proposed.
- Code is system-assigned and not client-writable: Accept proposed.
- Description is optional free text; detailed taxonomy remains deferred.
- Owner/salesperson fields are deferred; any future owner must not authorize.

## Risks

Medium — Legacy permits standalone requirements and weak cross-object
consistency. C3 deliberately fails closed instead of inheriting that behavior.

## Recommendation

Accept Design Boundary for C3 only.

## Product Owner response

**Approve — 2026-07-24 (conversation preauthorization; design boundary only).**
