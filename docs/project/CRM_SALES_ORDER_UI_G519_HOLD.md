# PHX-G519 HOLD RESOLVED — Sales Order Read-only UI

> Recorded 2026-07-29 under ADR-0321.

## Status

- Coding Authorization: **Consumed by PHX-G519**
- Milestone: **PHX-G519 COMPLETE**
- Queue: **RESOLVED**

## Blocker

Smart Terminal Sales Order read-only UI required a tenant-scoped Sales Order
collection query. Existing Gateway contracts previously provided only:

- `GET /v1/crm/sales-orders/{sales_order_id}`
- `GET /v1/crm/sales-orders/{sales_order_id}/lines`

## Disposition

Resolved through the accepted list-query Gate and PHX-G519 Coding Authorization.
`GET /v1/crm/sales-orders` is now available. No authority extends to G520+.

## Evidence

- `api/gateway/routers/crm.py`
- [Sales Order Read-only UI Gate](CRM_SALES_ORDER_READONLY_UI_ARCHITECTURE_GATE.md)
- [List Gate](CRM_SALES_ORDER_LIST_QUERY_ARCHITECTURE_GATE.md)
- [PHX-G519 Acceptance](CRM_SALES_ORDER_UI_G519_ACCEPTANCE.md)
