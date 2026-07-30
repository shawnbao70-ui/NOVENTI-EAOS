# Coding Authorization Summary — FX on Cash Events (G350)

## Milestone

**PHX-G350** — ADR-0317.3 transaction FX on receipt/AP payment.

## Alembic

**`0075_finance_fx_cash_events_g350`** revising
`0074_crm_fulfillment_qty_g349`.

## Authorized

1. ARReceipt and ApPayment store optional/required-when-enabled:
   `transaction_currency`, `functional_currency`, `fx_rate`, `functional_amount`
   (or document single-currency default: if currencies equal, fx_rate=1).
2. Create paths capture FX; reject missing rate when transaction ≠ functional
   (tenant functional currency from policy or request field).
3. HTTP schemas expose FX fields; contracts cover same-currency default and
   cross-currency require rate.
4. Do not expand live FX network; GL4 revaluation remains separate.

## Out

Baseline hygiene (G351), Cap widen, Brain silent writes, bank file import.

## Product Owner response

**Approve — batch; auto-continue G351.**
