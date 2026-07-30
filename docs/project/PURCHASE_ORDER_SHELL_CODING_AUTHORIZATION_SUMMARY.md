# Coding Authorization Summary — Purchase Order Shell (AP3)

## Milestone

**PHX-G332** — AP3, batch “AP3 / AP4 / AP5”; tip `0061`.

## Alembic

**`0062_purchase_order_shell_g332`** revising `0061_crm_return_restock_g330`.

## Authorized

Package `noventi.purchase`: draft Purchase Order header (supplier, code, currency,
idempotency), create/get (+ archive optional), Alembic `0062`, HTTP
`/v1/purchase/purchase-orders`, Permission/audit, contracts + gateway G332.
No receive, match, payment, GL, Brain/Twin.

## Out

AP4/AP5 (follow in batch after green), payment, PSP, Brain/Twin.

## Product Owner response

**Approve — 2026-07-26 batch “AP3 / AP4 / AP5” includes AP3.**  
Auto-continue to AP4 after TRACK-AP3 COMPLETE.
