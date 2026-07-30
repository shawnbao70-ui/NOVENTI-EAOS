# Decision Summary — CRM Business UI Serial AK→AR

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Business UI Serial AK→AR

## Purpose

Continue the governed CRM commercial-chain UI through eight strictly serial
frontend slices after FINAL STOP TRACK-G519.

## Scope

Design boundaries for Sales Order confirm, Customer 360, Quote Issue, Delivery
Order, AR Invoice issue, Return Authorization, AR Invoice void, and Customer
commercial hold UI slices. Candidates PHX-G520–G527. Absorbs the remaining
closed AC→AJ range G520–G525 and extends two further CRM slices.

## Architecture Boundary

CRM Package-owned Smart Terminal UI over existing APIs. Server Permission,
trusted Tenant context, audit correlation, lifecycle rules, optimistic
concurrency, and high-impact confirmation remain authoritative. Each slice is
independently gated and coded. Contiguous PHX-G numbering; no parallel second
milestone. Finance GL, Brain, and Twin remain hard-closed unless separately
authorized.

## In Scope

1. G520 candidate — Sales Order Confirm UI
2. G521 candidate — Customer 360 Read-only Composition
3. G522 candidate — Quote Issue UI
4. G523 candidate — Delivery Order Read / Release UI
5. G524 candidate — AR Invoice Read / Issue UI
6. G525 candidate — Return Authorization Read-only UI
7. G526 candidate — AR Invoice Void UI
8. G527 candidate — Customer Commercial Hold UI
9. Strict serial ordering, frontend contracts, browser evidence, and per-slice
   governance

## Out of Scope

- Finance GL posting, PSP/network activation, bank-file import, Brain, Twin,
  Purchase, Inventory, Marketplace expansion
- Credit-note GL posting beyond existing CRM RA/credit APIs
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
5. High-impact transitions (Confirm, Issue, Release, Void, Commercial Hold)
   require explicit UI confirmation and existing approval-policy contracts
   where applicable.
6. Final candidate stop is TRACK-G527.
7. Prior AC→AJ design acceptance for G520–G525 remains historical; AK→AR is
   the active serial plan from tip G519.

## Risks

- Existing APIs or list/collection gaps may force HOLD.
- Broad batch language may be mistaken for coding authority.
- Confirm / Issue / Release / Void / Hold are high-impact business transitions.
- Customer 360 and AR Invoice may accidentally widen PII or Finance scope.
- Serial numbering can drift if another milestone is legitimately opened.

## Recommendation

Approve the serial design plan while retaining `Coding Authorization: None`.
Start with an independent G520 Sales Order Confirm UI Decision Summary.
