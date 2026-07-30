# Decision Summary — CRM Quote Convert (C5)

> ADR-0321 decision surface; ADR-0312 rewrite boundary applies.

## Purpose

Define Convert as a tenant-safe, idempotent conversion instruction over an
existing Quote. C5 does not create a Sales Order.

## Gate In

- One immutable conversion instruction per same-tenant active Quote
- Client idempotency key, frozen quote version, Requirement and currency trace
- `ready` status; opaque ID; Permission resource `pkg.crm.quote_conversion`
- Audited create/read; no silent Quote mutation

## Gate Out

Sales Order creation, line/amount/term propagation, approval/publication,
Finance/AR/PSP, inventory/fulfillment, commissions and runtime events.

## Decisions

- Convert and SO creation are separate gates: Accept.
- Quote may be a C4 draft shell; conversion records intent only and makes no
  priced/approved commercial claim: Accept.
- One conversion per Quote is DB-authoritative; retry with the same key returns
  the same result, a different key conflicts: Accept.
- C6 must reject stale quote versions: Accept proposed.

## Product Owner response

**Approve — 2026-07-24 conversation preauthorization (design only).**
