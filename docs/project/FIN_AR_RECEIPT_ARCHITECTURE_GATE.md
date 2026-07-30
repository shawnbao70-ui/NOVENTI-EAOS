# Finance AR Receipt Shell Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0337  
**证据：** `FIN_AR_RECEIPT_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Package ownership: `noventi.finance` / `pkg.finance.receipt`; not Kernel.
2. Receipt statuses are `draft` and `applied` only; no bank settle.
3. Apply requires same-tenant issued (non-voided) AR Invoice via ReadPort.
4. Amount ≤ invoice total; currency match; tenant isolation; idempotent create/apply.
5. Permission default-deny; audit details empty (no PAN/PSP secrets).
6. Single-invoice apply only — not a multi-invoice allocation engine.

## Decision

Accepted through Product Owner conversation authorization (Wave R / F1).
