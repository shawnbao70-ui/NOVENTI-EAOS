# Coding Authorization Summary — Finance GL Bank Reconciliation (GL5)

## Milestone

**PHX-G323** — GL5, following PHX-G322 / GL4.

## Alembic

**`0057_finance_gl_bank_recon_g323`** revising `0056_finance_gl_fx_revaluation_g322`.

## Authorized

Package `noventi.finance`: bank statement shell + match/clear against journal
lines or receipt references (minimal); open-period awareness; no PSP live
network / F3; HTTP under `/v1/finance/bank-statements` (+ match/clear);
contracts + gateway G323. Final tip `0057`.

## Out

RET/AP/Z3/F3, live PSP, Brain/Twin, ENABLE_*_NETWORK live transport.

## Product Owner response

**Approve — 2026-07-26 batch “GL 收尾串行” includes GL5.**  
Auto-stop at TRACK-GL5 COMPLETE; await PO for PARKED items.
