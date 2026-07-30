# PHX-G350 — FX on Cash Events Summary

System-generated implementation summary for the approved FX on Cash Events
boundary (ADR-0382).

- Alembic tip: `0075_finance_fx_cash_events_g350`.
- Finance AR receipts and Purchase AP payments persist functional currency, FX
  rate, and functional amount.
- Same-currency events default to rate `1` and the transaction amount.
- Cross-currency events fail closed without a positive FX rate; the functional
  amount is derived and quantized from the transaction amount and rate, or
  rejected when a supplied amount disagrees.
- No live FX network, FX revaluation, or GL-posting scope was added.
