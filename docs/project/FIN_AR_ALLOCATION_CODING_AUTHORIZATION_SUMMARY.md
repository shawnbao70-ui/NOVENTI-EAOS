# Coding Authorization Summary — AR Allocation Engine Shell (G342)

## Milestone

**PHX-G342** — explicit AR receipt allocation (ADR-0315).

## Alembic

**`0069_finance_ar_allocation_g342`** revising
`0068_purchase_ap_partial_payment_g341`.

## Compatibility strategy

Keep `POST .../receipts/{id}/apply` as a convenience that creates a single
allocation for the full receipt amount (or remaining) against one invoice —
same Permission surface. New explicit allocation API supports partial and
multi-allocation; receipt status becomes applied only when allocated_amount
covers receipt amount (or document clearly: first apply marks applied with
partial allocated_amount tracked).

Preferred model:
- `finance.ar_receipt_allocations` lines (receipt_id, invoice_id, amount, key)
- Receipt gains `allocated_amount`; unallocated = amount − allocated_amount
- `apply_receipt_to_invoice` creates one allocation line (idempotent); may be
  partial if amount arg or receipt residual

## Authorized

Partial/multi allocate to issued AR invoices; query unallocated; over-allocate
fail-closed; Permission + audit; HTTP + contracts.

## Out

AP, CN/RMA, tax, Cap→grant, Brain silent writes.

## Product Owner response

**Approve — batch includes G342.** Auto-continue to G343.
