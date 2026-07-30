# Coding Authorization Summary — Three-Way Match Shell (AP5)

## Milestone

**PHX-G334** — AP5, following PHX-G333 / AP4.

## Alembic

**`0064_purchase_three_way_match_g334`** revising
`0063_purchase_goods_receipt_inventory_g333`.

## Authorized

Package `noventi.purchase`: ThreeWayMatch linking PO + GRN + draft ApBill
(with lines), status `matched|mismatch`, unique per tenant+PO, idempotent,
fail-closed supplier/lineage checks, amount/qty comparison policy, HTTP
`POST /v1/purchase/three-way-matches`, contracts + gateway G334.
No payment, PSP, GL post, Brain/Twin.

## Out

Payment run, PSP, GL, partial match v2, tax engine, Brain/Twin.

## Product Owner response

**Approve — 2026-07-26 batch “AP3 / AP4 / AP5” includes AP5.**  
Auto-stop at TRACK-AP5 COMPLETE.
