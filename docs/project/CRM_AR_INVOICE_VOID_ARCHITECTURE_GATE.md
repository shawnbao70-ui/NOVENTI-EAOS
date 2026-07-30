# CRM AR Invoice Void Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0336  
**证据：** `CRM_AR_INVOICE_VOID_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Issued→Voided is explicit, auditable, and human-confirmed.
2. Reason is required (1..500) and stored on the entity.
3. Same void key replays; different key conflicts.
4. Draft cannot void; voided cannot re-issue.
5. Voided ≠ credit memo ≠ GL reverse; no cascade to DO/SO/Quote.
6. C12 confirm-approval policy is not applied to void.

## Decision

Accepted through Product Owner conversation authorization.
