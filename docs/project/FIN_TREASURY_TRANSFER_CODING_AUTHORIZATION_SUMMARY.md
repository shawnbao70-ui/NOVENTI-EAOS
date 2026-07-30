# Coding Authorization Summary — Treasury Transfer + FX (G371)

## Milestone

**PHX-G371** — ADR-0317.3 treasury/cash transfer event with FX.

## Alembic

**`0091_finance_treasury_transfer_g371`** revising `0090_…`.

## Authorized

1. `TreasuryTransfer` (or `CashTransfer`) shell in finance: from_account_ref,
   to_account_ref (UUID or code strings), amount, currency,
   functional_currency, fx_rate, functional_amount, status draft|posted,
   idempotency_key.
2. Same FX rules as G350 cash events; post with human_confirm.
3. HTTP under `/v1/finance/treasury-transfers`; no bank file import; no PSP.
4. Contracts.

## Out

FX-GL bridge (G372), DE, host installs.

## Product Owner response

**Approve — batch; auto-continue G372.**
