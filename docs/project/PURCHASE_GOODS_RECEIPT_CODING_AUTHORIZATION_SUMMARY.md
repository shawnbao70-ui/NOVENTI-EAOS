# Coding Authorization Summary — PO Goods Receipt + Inventory (AP4)

## Milestone

**PHX-G333** — AP4, following PHX-G332 / AP3.

## Alembic

**`0063_purchase_goods_receipt_inventory_g333`** revising
`0062_purchase_order_shell_g332`.

## Authorized

Package `noventi.purchase` + inventory receive port: minimal PO lines
(inventory_item_id, qty), GoodsReceipt create with human_confirm + idempotency,
same-UoW inventory on_hand++ / `PO_RECEIVE` ledger, one GRN per PO, HTTP
`POST /v1/purchase/purchase-orders/{id}/goods-receipt`, contracts + gateway G333.
No three-way match, payment, auto AP Bill, client qty override, Brain/Twin.

## Out

AP5 (next in batch), payment, PSP, GL, partial receive, quarantine WMS.

## Product Owner response

**Approve — 2026-07-26 batch “AP3 / AP4 / AP5” includes AP4.**  
Auto-continue to AP5 after TRACK-AP4 COMPLETE.
