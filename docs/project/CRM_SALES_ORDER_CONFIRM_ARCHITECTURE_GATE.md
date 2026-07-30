# CRM Sales Order Confirmation Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0328

## Invariants

1. Human confirmation must be explicit.
2. Sales Order is `created` and conversion trace exists.
3. Quote version equals the conversion snapshot.
4. At least one active Quote Line exists.
5. SO line snapshots, total and status transition are one transaction.
6. Same-key retry is idempotent; another key conflicts.
7. Confirmation implies no Finance, inventory or fulfillment action.

## Decision

Accepted through Product Owner conversation authorization.
