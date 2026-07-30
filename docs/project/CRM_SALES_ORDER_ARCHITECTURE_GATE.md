# CRM Sales Order Trace Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0312, ADR-0325, ADR-0326

## Invariants

1. A `ready` same-tenant conversion is mandatory.
2. Quote must remain active at its frozen version.
3. One conversion and one Quote yield at most one SO.
4. SO insert and conversion consumption are one transaction.
5. Same-key retry is idempotent; another key conflicts.
6. Permission is default-deny and creation is audited.

## Gate Out

Lines/amounts/terms, Finance/AR/PSP, inventory, fulfillment/shipping,
commissions and events.

## Decision

Accepted through Product Owner conversation preauthorization.
