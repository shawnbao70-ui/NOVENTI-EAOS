# Coding Authorization Summary — Finance Tax Rate + Authority Port (Tax2)

## Milestone

**PHX-G317** — Tax2, following PHX-G316 / Tax1.

## Alembic

**`0052_finance_tax_rate_authority_port_g317`** revising
`0051_finance_tax_invoice_shell_g316`.

## Authorized

Package `noventi.finance`: tenant-scoped tax rate registry (code/name/rate/status),
fail-closed `TaxAuthorityPort` (RejectAll default + test-only Fake), opt-in
authority validation policy, no live filing / network, permissioned/audited
HTTP for tax rates + tax-authority policy, contracts + gateway G317 tests.
OpenAPI must not expose filing, `ENABLE_*_NETWORK`, GL/journal, or Tax3 adapter
surfaces on this slice.

## Out

Tax3 authority adapter, live tax authority filing, `ENABLE_*_NETWORK`,
GL/CoA/journal/period, Brain/Twin, Tax3+.

## Prerequisites

- TRACK-TAX1 COMPLETE; Alembic tip `0051_finance_tax_invoice_shell_g316`
- ADR-0316 rewrite boundary; F2 PspPort pattern (fail-closed port + policy)
- Design inventory from Post-CRM queue

## Product Owner response

**Approve — 2026-07-26 explicit “Tax2（PHX-G317 / 0052）” authorization.**  
Milestone: **PHX-G317**. Auto-stop at TRACK-TAX2 COMPLETE; await Tax3.
