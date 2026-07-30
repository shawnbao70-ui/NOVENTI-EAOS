# Coding Authorization Summary — Convert Terms + FX Snapshot (G352)

## Milestone

**PHX-G352** — ADR-0312 + ADR-0317.2 Quote→SO FX/terms snapshot.

## Alembic

**`0076_crm_convert_fx_snapshot_g352`** revising
`0075_finance_fx_cash_events_g350`.

## Authorized

1. Quote may hold optional `fx_rate` / `functional_currency` (or accept on
   convert request); Convert persists snapshot onto SalesOrder (and
   QuoteConversion): `currency`, `functional_currency`, `fx_rate`,
   `functional_total` (or equivalent).
2. Same-currency default fx_rate=1; cross-currency requires fx_rate > 0
   fail-closed.
3. Convert HTTP exposes/accepts FX fields; envelopes show snapshot on SO.
4. Contracts. No approval wiring (G353), no commission (G356).

## Out

G353–G357 scopes; Brain silent writes; host installs.

## Product Owner response

**Approve — Constitution closeout II batch.** Auto-continue G353.
