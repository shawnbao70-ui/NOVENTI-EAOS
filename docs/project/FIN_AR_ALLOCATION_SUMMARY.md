# Finance AR Allocation Summary — PHX-G342

**Status:** implemented under the approved coding authorization and ADR-0374.

AR receipt settlement is represented by immutable, tenant-scoped allocation
lines. A receipt may be partially allocated across multiple issued invoices of
the same customer and currency. `allocated_amount` is persisted on the receipt;
`unallocated_amount` is derived as `amount - allocated_amount`.

The compatibility `POST /v1/finance/receipts/{receipt_id}/apply` path creates
one allocation for the full remaining receipt balance. For compatibility,
`ar_invoice_id` remains the **first** allocated invoice; it is not overwritten
by later allocations. A receipt changes to `applied` only when fully allocated.

The allocation key is tenant-unique and idempotent. Over-allocation, missing
receipts, unissued invoices, tenant/customer/currency mismatches all fail
closed. This slice does not add AR posting, PSP settlement, tax, credit-note,
AP, Brain, or Twin behavior.
