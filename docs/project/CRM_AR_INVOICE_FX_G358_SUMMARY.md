# PHX-G358 — AR Invoice FX from SO

- Added Alembic revision `0081_crm_ar_invoice_fx_g358`, backfilling `crm.ar_invoices.functional_currency`, `fx_rate`, and `functional_total` from the invoice transaction currency and total with rate `1`.
- AR Invoice creation now snapshots the Sales Order functional currency and FX rate, and recomputes the invoice functional total as `invoice.total_amount × so.fx_rate` rounded to two decimals.
- AR Invoice envelopes expose the immutable FX snapshot. Missing cross-currency SO FX fails closed; same-currency legacy SOs default to rate `1`.
- No realized FX allocation, Finance posting, Brain, or Twin scope was introduced; that work remains PHX-G359.

Tip verified: `0081_crm_ar_invoice_fx_g358`
