# Coding Authorization Summary — CRM Return Authorization Shell (RET1)

## Milestone

**PHX-G325** — RET1, following PHX-G324 / AP1 (tip `0058`).

## Alembic

**`0059_crm_return_authorization_g325`** revising
`0058_purchase_supplier_ap_bill_g324`.

## Authorized

Package `noventi.crm`: tenant-scoped Return Authorization documentary shell
against a **shipped** Delivery Order (optional same-lineage AR invoice),
status=`draft` only, create/get with human_confirm + idempotency, unique per
`(tenant, delivery_order_id)` and `(tenant, idempotency_key)`, Alembic `0059`,
HTTP `POST /v1/crm/delivery-orders/{id}/return-authorizations` and
`GET /v1/crm/return-authorizations/{id}`, Permission/audit, contracts + gateway
G325 tests. No restock, auto credit-note, PSP refund, or Brain/Twin.

## Out

RET2 restock/putaway, quarantine WMS, auto credit-note, PSP refund, commission
clawback, carrier labels, Brain execute / Twin authorize, AP2–AP5, F3.

## Prerequisites

- Tip `0058_purchase_supplier_ap_bill_g324`; I1 DO Ship + CRM DO/AR exist
- Legacy return gap knowledge (input only)

## Product Owner response

**Approve — 2026-07-26 explicit “RET1（RMA）” authorization.**  
Milestone: **PHX-G325**. Auto-stop at TRACK-RET1 COMPLETE; await RET2 or other PO pick.
