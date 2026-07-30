# Finance AR Credit Note Shell Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0339  
**证据：** `FIN_AR_CREDIT_NOTE_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Package ownership: `noventi.finance` / `pkg.finance.credit_note`.
2. Statuses are `draft` and `issued` only; issued ≠ GL posted.
3. Create requires same-tenant AR Invoice in `issued` or `voided`.
4. Amount ≤ invoice total; currency/customer inherited from invoice; idempotent.
5. Permission default-deny; audit details empty (no commercial secrets).
6. No journal, CoA, tax-authority, or PSP refund surfaces.

## Decision

Accepted through Product Owner conversation authorization (Wave N / N1).
