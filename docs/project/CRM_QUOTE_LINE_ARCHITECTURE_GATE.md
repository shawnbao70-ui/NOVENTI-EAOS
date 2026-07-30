# CRM Quote Line Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0327

## Invariants

1. Parent Quote is active, draft and same-tenant.
2. Quantity is positive; unit price is non-negative.
3. Amount is server-computed and never client-writable.
4. Line mutation and Quote version increment are one transaction.
5. Permission is default-deny; audit omits text and money.
6. No pricing, Finance, inventory or fulfillment capability is implied.

## Decision

Accepted through Product Owner conversation authorization.
