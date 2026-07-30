# ADR-0325 — CRM Quote Convert Product Boundary

**状态：** Accepted（design boundary only）  
**日期：** 2026-07-24  
**上位边界：** ADR-0312

## Decision

C5 persists a `QuoteConversion` instruction for one active same-tenant Quote.
It freezes `quote_version`, Requirement trace and currency label. A unique
tenant/Quote constraint and client idempotency key prevent duplicate commands.

The instruction starts `ready`. C5 does not update Quote status and does not
create a Sales Order. A future C6 transaction may consume it only while the
Quote still matches the frozen version.

Permission is default-deny (`pkg.crm.quote_conversion`, `convert`/`read`).
Create intent/result are audited without commercial notes or idempotency key.

## Out

SO CRUD, pricing/lines/terms, publication/approval, Finance/AR/PSP,
fulfillment/inventory, commissions, AI/Brain/Twin and runtime events.
