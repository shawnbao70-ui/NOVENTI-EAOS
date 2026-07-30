# ADR-0327 — CRM Quote Line Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24

## Decision

C7 introduces `QuoteLine` as a child of an active draft Quote. It stores a
description, positive decimal quantity, non-negative manual unit-price
snapshot and server-calculated amount. Currency remains on the Quote.

Every create/update/archive operation updates the Quote version in the same
transaction. Therefore a C5 conversion instruction created before a line
change cannot be consumed by C6/C8.

Permission is default-deny (`pkg.crm.quote_line`). Write intent/result audits
exclude description and monetary values.

## Out

Catalog/product lookup, cost/margin, tax/discount, FX calculation, pricing
rules, inventory, approval, Finance/AR/PSP and fulfillment.
