# PHX-G359 — Realized FX on Allocation

- Added system-generated governance implementation artifact: Alembic
  `0082_finance_realized_fx_allocation_g359`, which creates the tenant-scoped,
  immutable `finance.realized_fx_events` audit table.
- Cross-currency receipt allocations now require positive receipt and invoice FX
  snapshots in the same functional currency. The allocation amount is converted
  by each snapshot; `receipt_functional - invoice_functional` is the realized
  delta (positive = gain, negative = loss).
- A non-zero cross-currency delta persists one allocation-linked realized FX
  event. Same-currency behavior remains unchanged and zero deltas have no
  gain/loss event or side.
- Allocation envelopes expose `realized_fx_amount` and `realized_fx_side`.
  This slice intentionally persists the audit event only; it does not post GL.

Tip verified: `0082_finance_realized_fx_allocation_g359`
