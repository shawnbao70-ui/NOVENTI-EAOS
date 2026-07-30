# ADR-0329 — CRM Delivery Order Shell Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**上位边界：** ADR-0314

## Decision

C9 creates one tenant-scoped `DeliveryOrder` shell from a confirmed Sales
Order. It freezes upstream IDs, currency and confirmed total, and remains
`draft`.

Because C9 has no allocation or remaining-quantity model, a unique
tenant/Sales-Order constraint forbids duplicate shells. This is a deliberate
safe subset of ADR-0314, not a claim that partial fulfillment exists.

Permission is default-deny. Create intent/result audit details exclude
commercial values and keys.

## Out

Lines, quantity allocation, WMS, inventory mutation, shipping, carrier/POD,
returns, Finance/AR posting, PSP and events.
