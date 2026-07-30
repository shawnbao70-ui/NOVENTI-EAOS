# CRM Quote Convert Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0312, ADR-0325

## Invariants

1. Active same-tenant Quote is mandatory.
2. One Quote has at most one conversion instruction.
3. Same idempotency key retries return the existing instruction; another key
   conflicts.
4. Quote version, Requirement and currency are frozen explicitly.
5. Convert never silently changes Quote and never creates SO in C5.
6. Permission is default-deny and the write is audited.

## Gate Out

Sales Order, commercial terms/lines/amounts, approval, Finance/AR/PSP,
inventory/fulfillment, commissions and events.

## Decision

Accepted through Product Owner conversation preauthorization.
