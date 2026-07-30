# Coding Authorization Summary — Purchase AP Bill Lines (AP2)

## Milestone

**PHX-G329** — AP2, following tip `0059` / batch “AP2 / RET2”.

## Alembic

**`0060_purchase_ap_bill_line_g329`** revising
`0059_crm_return_authorization_g325`.

## Authorized

Package `noventi.purchase`: draft AP Bill lines (quantity, unit_price, amount),
parent must remain `draft`, maintain `bill.total_amount` as sum of active lines,
HTTP `/v1/purchase/ap-bills/{id}/lines`, Permission/audit, contracts + gateway
G329. No issue/post/pay/PO/GR/tax/GL/PSP/Brain/Twin.

## Out

AP3–AP5, payment, RET2 (separate slice), Brain/Twin.

## Product Owner response

**Approve — 2026-07-26 batch “AP2 / RET2” includes AP2.**  
Auto-continue to RET2 after TRACK-AP2 COMPLETE.
