# Coding Authorization Summary — Finance AR Credit Note Shell (N1)

## Milestone

**PHX-G312** — next free contiguous PHX-G after PHX-G311.

## Authorized

ADR-0339 Gate In only: credit note model/service/repository/persistence, Alembic
`0048_finance_ar_credit_note_g312`, gateway `/v1/finance/credit-notes`
create/get/issue, Permission/audit, contracts + gateway G312 + PostgreSQL tests.
OpenAPI must not expose gl/journal/psp-refund/tax-filing surfaces on the credit
note slice.

## Out

GL/CoA/journal/period close, tax authority credit, PSP refund execution,
multi-invoice credit application, write-off automation, Brain/Twin, Z1+.

## Prerequisites

- TRACK-I1 COMPLETE; Alembic tip `0047_inventory_do_ship_g311`
- Design Gate Accepted (this conversation)

## Product Owner response

**Approve — 2026-07-25 conversation authorization.**  
Milestone: **PHX-G312**. Auto-stop at TRACK-N1 COMPLETE; await Z1.
