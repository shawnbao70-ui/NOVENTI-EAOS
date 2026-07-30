# Coding Authorization Summary — CRM Customer360 Read Projection (Z1)

## Milestone

**PHX-G313** — next free contiguous PHX-G after PHX-G312.

## Authorized

ADR-0340 Gate In only: Customer360 service/assembler, gateway
`GET /v1/crm/customers/{customer_id}/360`, Permission/audit-free read path,
contracts + gateway G313 + PostgreSQL read case. Zero Alembic revision
(prefer live assemble). OpenAPI must not expose
brain/execute/twin/authorize/commission/payout on the 360 surface.

## Out

Commission ledger (Z2), Brain/Twin authorize, write APIs from 360, CDP sync,
and any tip bump that invents `0049` without a projection table need.

## Prerequisites

- TRACK-N1 COMPLETE; Alembic tip `0048_finance_ar_credit_note_g312`
- Design Gate Accepted (this conversation)

## Product Owner response

**Approve — 2026-07-25 conversation authorization.**  
Milestone: **PHX-G313**. Auto-stop at TRACK-Z1 COMPLETE; end four-wave program.
