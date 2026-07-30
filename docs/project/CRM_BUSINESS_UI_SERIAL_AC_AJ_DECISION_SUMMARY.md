# Decision Summary — CRM Business UI Serial AC→AJ

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Business UI Serial AC→AJ

## Purpose

Continue the governed CRM commercial-chain UI through eight strictly serial
frontend slices after FINAL STOP TRACK-G517.

## Scope

Design boundaries for Quote Convert, Sales Order read, Sales Order confirm,
Customer 360, Quote Issue, Delivery Order, AR Invoice, and Return Authorization
UI slices. Candidates PHX-G518–G525.

## Architecture Boundary

CRM Package-owned Smart Terminal UI over existing APIs. Server Permission,
trusted Tenant context, audit correlation, lifecycle rules, optimistic
concurrency, and high-impact confirmation remain authoritative. Each slice is
independently gated and coded. Contiguous PHX-G numbering; no parallel second
milestone.

## In Scope

1. G518 candidate — Quote Convert UI
2. G519 candidate — Sales Order Read-only UI
3. G520 candidate — Sales Order Confirm UI
4. G521 candidate — Customer 360 Read-only Composition
5. G522 candidate — Quote Issue UI
6. G523 candidate — Delivery Order Read / Release UI
7. G524 candidate — AR Invoice Read / Issue UI
8. G525 candidate — Return Authorization Read-only UI
9. Strict serial ordering, frontend contracts, browser evidence, and per-slice
   governance

## Out of Scope

- Finance GL posting, credit notes beyond existing CRM RA/credit APIs, Brain,
  Twin, Purchase, Inventory, Marketplace expansion
- External network/PSP activation, bank-file import, automatic/bulk writes
- Database, Alembic, Kernel, Runtime Manifest changes unless a slice has its
  own independent Coding Authorization that explicitly allows a prerequisite
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
5. High-impact transitions (Convert, Confirm, Issue, Release) require explicit
   UI confirmation and existing approval-policy contracts where applicable.
6. Final candidate stop is TRACK-G525.

## Risks

- Existing APIs or list/collection gaps may force HOLD.
- Broad batch language may be mistaken for coding authority.
- Convert / Confirm / Issue / Release are high-impact business transitions.
- Customer 360 and AR Invoice may accidentally widen PII or Finance scope.
- Serial numbering can drift if another milestone is legitimately opened.

## Recommendation

Approve the serial design plan while retaining `Coding Authorization: None`.
Start with an independent G518 Quote Convert UI Decision Summary.
