# Coding Authorization Summary — AR Invoice FX from SO (G358)

## Milestone

**PHX-G358** — ADR-0317.2 propagate SO FX snapshot onto AR Invoice.

## Alembic

**`0081_crm_ar_invoice_fx_g358`** revising
`0080_finance_commission_status_g356`.

## Authorized

1. ARInvoice gains `functional_currency`, `fx_rate`, `functional_total`.
2. On create from DO/SO: copy SO snapshot (same-currency default fx_rate=1);
   fail-closed if SO missing FX when currencies would require it (SO always
   has fields after G352 backfill).
3. Envelopes expose fields; contracts; no realized FX yet (G359).

## Out

G359–G363 scopes; Brain silent writes.

## Product Owner response

**Approve — Constitution closeout III.** Auto-continue G359.
