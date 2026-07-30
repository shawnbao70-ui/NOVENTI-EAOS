# CRM Delivery Order Release Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0334  
**证据：** `CRM_DELIVERY_ORDER_RELEASE_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Draft→Released is explicit, auditable, and human-confirmed.
2. Release requires confirmed SO and clear commercial hold.
3. Same release key replays; different key conflicts.
4. AR invoice shell create requires released DO.
5. No inventory / ship / packing / carrier side effects.
6. No cancel/reopen in this slice.

## Decision

Accepted through Product Owner conversation authorization.
