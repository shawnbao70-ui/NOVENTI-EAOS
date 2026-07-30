# Decision Summary — CRM Business UI Serial U→AB

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated artifacts are not Product
> Owner editing surfaces.

## Package

CRM — Business UI Serial U→AB

## Purpose

Complete the governed CRM commercial-chain user experience through eight
strictly serial frontend slices.

## Scope

Design boundaries for Opportunity, Requirement, Quote header, Quote lines,
Quote conversion, Sales Order read, Sales Order confirmation, and Customer 360
read-only composition.

## Architecture Boundary

CRM Package-owned Smart Terminal UI over existing APIs. Server Permission,
trusted Tenant context, audit correlation, lifecycle rules, and optimistic
concurrency remain authoritative. Each slice is independently gated and coded.

## In Scope

1. G514 candidate — Opportunity Managed UI
2. G515 candidate — Requirement Managed UI
3. G516 candidate — Quote Header Managed UI
4. G517 candidate — Quote Lines Managed UI
5. G518 candidate — Quote Convert UI
6. G519 candidate — Sales Order Read-only UI
7. G520 candidate — Sales Order Confirm UI
8. G521 candidate — Customer 360 Read-only Composition
9. Strict serial ordering, frontend contracts, browser evidence, and per-slice
   governance

## Out of Scope

- API, Service, Repository, Database, Alembic, or Runtime Manifest changes
- Finance, Brain, Twin, Purchase, Inventory, or Marketplace expansion
- External network/PSP activation, bank-file import, automatic/bulk writes
- Hard delete, permission bypass, production promotion
- Parallel milestones or automatic opening of a blocked successor

## Open Decisions

1. Each slice must have an independent Decision Summary and Product Owner
   design decision.
2. Each accepted slice retains `Coding Authorization: None` until separately
   approved.
3. A missing backend prerequisite places the current slice on HOLD and stops
   the serial queue.
4. Candidate milestone numbers remain unopened until Coding Authorization.
5. Final candidate stop is TRACK-G521.

## Risks

- Existing APIs may not support a planned UI slice.
- Broad batch language may be mistaken for coding authority.
- Quote conversion and Sales Order confirmation are high-impact business
  transitions.
- Customer 360 can accidentally widen PII or adjacent-domain scope.
- Serial numbering can drift if another milestone is legitimately opened.

## Recommendation

Approve the serial design plan while retaining `Coding Authorization: None`.
Start with an independent G514 Opportunity Managed UI Decision Summary.
