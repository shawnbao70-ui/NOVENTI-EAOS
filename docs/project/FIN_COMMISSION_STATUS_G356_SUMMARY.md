# PHX-G356 — Commission status deepen

- Added Alembic revision `0080_finance_commission_status_g356`, expanding the Finance commission status constraint to `accrued`, `payable`, and `paid`.
- Commission transitions are explicit, permissioned (`update` on `pkg.finance.commission`), audited, optimistic-versioned commands: `accrued → payable → paid`. All skipped or repeated transitions fail closed with conflict.
- HTTP provides `POST /v1/finance/commissions/{id}/payable` and `/paid`; existing GET reflects the current status.
- The GL commission-accrue bridge remains intentionally restricted to `accrued`. A payable or paid commission is rejected from that bridge, preventing a subsequent status transition from creating a duplicate accrual posting.
- No payout PSP, payroll, clawback, Brain, or Twin surface was introduced.

Tip verified: `0080_finance_commission_status_g356`
