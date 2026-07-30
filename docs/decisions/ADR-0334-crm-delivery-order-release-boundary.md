# ADR-0334 — CRM Delivery Order Release Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-25  
**里程碑（coding）：** PHX-G307

## Decision

C14 adds DeliveryOrder status `released` and `release_delivery_order` as a
local release command. Release requires human confirmation, a confirmed Sales
Order, and a commercially clear customer (C11 helper). It is idempotent by
`release_key` and authorized by default-deny action `release` on
`pkg.crm.delivery_order`.

`create_ar_invoice` accepts only released delivery orders. This is not WMS
ship, inventory deduction, packing, carrier tracking, or Invoice issue/post.

## Out

WMS/inventory, ship qty, packing/carrier, PSP, GL, AR invoice issue/post,
Approval Center expansion, email/PDF, Brain/Twin, and C15+.
