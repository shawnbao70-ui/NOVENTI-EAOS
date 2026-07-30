# Coding Authorization Summary — Finance AR Receipt Shell (F1)

## Milestone

**PHX-G310** — next free contiguous PHX-G after PHX-G309.

## Authorized

ADR-0337 Gate In only: `noventi.finance` Receipt model/service/repository/
persistence, Alembic `0046_finance_ar_receipt_g310`, gateway
`/v1/finance/receipts` create/apply/get, Permission/audit, contracts + gateway
G310 + PostgreSQL tests. OpenAPI must not expose psp/ledger/gl/refund/write-off
surfaces on the Finance receipt slice.

## Out

Live PSP provider, full allocation engine, write-off/refunds/FX, GL, bank recon,
AP, tax filing, Brain/Twin, Inventory ship, Customer360 product, I1+.

## Prerequisites

- CRM C16 COMPLETE; Alembic tip `0045_crm_ar_invoice_void_g309` (or actual C16 tip)
- Design Gate Accepted (this conversation)

## Product Owner response

**Approve — 2026-07-25 conversation authorization.**  
Milestone: **PHX-G310**. Auto-stop at TRACK-F1 COMPLETE; await I1.
