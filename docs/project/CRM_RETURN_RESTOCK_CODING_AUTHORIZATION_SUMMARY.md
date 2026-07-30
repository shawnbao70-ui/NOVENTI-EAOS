# Coding Authorization Summary — CRM Return Restock Ledger (RET2)

## Milestone

**PHX-G330** — RET2, following PHX-G329 / AP2.

## Alembic

**`0061_crm_return_restock_g330`** revising
`0060_purchase_ap_bill_line_g329`.

## Authorized

Package `noventi.crm` + inventory restock port: transition Return Authorization
`draft → restocked` with human_confirm + idempotency; inventory `on_hand++` /
RMA restock ledger in same UoW; qty ≤ shipped net; full restock only; HTTP
`POST /v1/crm/return-authorizations/{id}/restock`; contracts + gateway G330.
No auto credit-note, PSP refund, quarantine WMS, Brain/Twin.

## Out

Auto CN, PSP refund, partial restock lines, putaway/quarantine, AP3+, Brain/Twin.

## Product Owner response

**Approve — 2026-07-26 batch “AP2 / RET2” includes RET2.**  
Auto-stop at TRACK-RET2 COMPLETE.
