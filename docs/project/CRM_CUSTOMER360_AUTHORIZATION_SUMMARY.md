# Decision Summary — CRM Customer360 Read Projection (Z1 / Wave Z)

> ADR-0321 decision surface; ADR-0340 boundary applies.
> System-generated governance artifact from PO conversation authorization.

## Package

`noventi.crm` — `pkg.crm.customer360` (read projection; not Kernel)

## Purpose

Read-only Customer360 aggregation over CRM facts plus Finance receipt/credit
traces when present. Presentation/query surface only.

## Scope

### Gate In

- `GET /v1/crm/customers/{customer_id}/360` closed envelope
- Live assemble: customer, opportunities count, open SO/DO counts, hold flag,
  invoice status traces, applied receipt refs, credit note refs
- Permission `read` on `pkg.crm.customer360` (default-deny)
- Zero-migration live read (no projection table)

### Gate Out

- Commission ledger / payout (future Z2 — separate PO instruction)
- Brain execute / Twin authorize / Cap→grant invent
- Write APIs mutating CRM/Finance from 360
- External CDP/marketing sync

## Major architectural decisions

- Prefer live assemble over cached projection table (Accept).
- Dedicated `pkg.crm.customer360` read action (not reuse customer read alone).
- Finance/Inventory facts observed via package persistence reads in the
  assembler — no write engines.

## Open decisions requiring Product Owner input

None for Z1 — locked by Wave Z instruction.

## Risks

- Open SO/DO counts depend on inventory ship postings when present; without a
  ship posting, released DOs remain “open”.

## Recommendation

Approve design boundary and authorize coding as PHX-G313.

## Product Owner response

**Approve — 2026-07-25 conversation authorization (design + coding PHX-G313).**
