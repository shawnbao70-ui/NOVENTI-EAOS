# CRM AR Invoice Issue Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0335  
**证据：** `CRM_AR_INVOICE_ISSUE_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Draft→Issued is explicit, auditable, and human-confirmed.
2. Issue requires released DO, confirmed SO, and clear commercial hold.
3. Same issue key replays; different key conflicts.
4. Issued ≠ posted; no GL/tax/payment side effects.
5. C12 confirm-approval policy is not applied to invoice issue.
6. No cancel/credit/void in this slice.

## Decision

Accepted through Product Owner conversation authorization.
