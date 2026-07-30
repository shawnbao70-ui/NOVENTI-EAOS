# ADR-0326 — CRM Sales Order Trace Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**上位边界：** ADR-0312, ADR-0325

## Decision

C6 creates a minimal `SalesOrder` trace header from one `ready`
`QuoteConversion`. The transaction verifies that the Quote is still active and
matches the frozen quote version, inserts exactly one Sales Order, and marks
the conversion `consumed`.

The Sales Order stores opaque ID, system code, conversion/Quote/Requirement
IDs, currency label, `created` status and idempotency key. It makes no line,
amount, fulfillment or receivable claim.

Permission is default-deny (`pkg.crm.sales_order`, `create`/`read`). The create
intent/result is audited without commercial or idempotency data.

## Out

Finance/AR/PSP, order lines and commercial terms, inventory, fulfillment,
shipment/delivery/returns, commissions, AI/Brain/Twin and runtime events.
