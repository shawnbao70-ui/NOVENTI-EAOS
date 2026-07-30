# Coding Authorization Summary — Inventory DO Ship Ledger (I1)

## Milestone

**PHX-G311** — next free contiguous PHX-G after PHX-G310.

## Authorized

ADR-0338 Gate In only: inventory stock/ledger/ship posting persistence, Alembic
`0047_inventory_do_ship_g311` (includes CRM DO status `shipped`), gateway ship +
stock adjust/read surfaces, Permission/audit, contracts + gateway G311 +
PostgreSQL tests; regress DO release / commercial hold.

## Out

External WMS/3PL, ASN/wave/lot/serial, transfers, RMA, manufacturing, Finance
postings, PSP, Brain/Twin, N1+.

## Prerequisites

- TRACK-F1 COMPLETE; Alembic tip `0046_finance_ar_receipt_g310`
- Design Gate Accepted (this conversation)

## Product Owner response

**Approve — 2026-07-25 conversation authorization.**  
Milestone: **PHX-G311**. Auto-stop at TRACK-I1 COMPLETE; await N1.
