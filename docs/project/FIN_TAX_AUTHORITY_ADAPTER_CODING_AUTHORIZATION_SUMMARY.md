# Coding Authorization Summary — Finance Tax Authority Adapter (Tax3)

## Milestone

**PHX-G318** — Tax3, following PHX-G317 / Tax2.

## Alembic

**None.** Tip remains `0052_finance_tax_rate_authority_port_g317`.
No adapter-config table in this slice.

## Authorized

Package `noventi.finance`: Network/HTTP `TaxAuthority` adapter skeleton,
env gate `EAOS_TAX_NETWORK` (alias `ENABLE_TAX_NETWORK`), default OFF →
`RejectAllTaxAuthority`; when ON without endpoint still fail-closed (no live
HTTP calls in this slice); optional read-only adapter status HTTP; wire into
`TransactionalFinanceService` / factory; contracts + gateway G318 tests.

## Out

Live filing, real tax authority HTTP calls, GL/CoA/journal/period, Brain/Twin,
F3 PSP network.

## Prerequisites

- TRACK-TAX2 COMPLETE; Alembic tip `0052_finance_tax_rate_authority_port_g317`
- ADR-0349 TaxAuthorityPort boundary; F2 PspPort fail-closed + opt-in pattern

## Product Owner response

**Approve — 2026-07-26 explicit “Tax3（PHX-G318）” authorization.**  
Milestone: **PHX-G318**. Auto-stop at TRACK-TAX3 COMPLETE; await GL1.
