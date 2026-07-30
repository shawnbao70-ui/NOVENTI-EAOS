# Coding Authorization Summary — Finance GL Chart + Journal (GL1)

## Milestone

**PHX-G319** — GL1, following PHX-G318 / Tax3.

## Alembic

**`0053_finance_gl_chart_journal_g319`** revising
`0052_finance_tax_rate_authority_port_g317`.

## Authorized

Package `noventi.finance`: tenant-scoped Chart of Accounts (`GlAccount`) and
Journal Entry shell (`draft → posted`, balanced lines, irreversible post),
Alembic `0053`, gateway `/v1/finance/gl-accounts` and
`/v1/finance/journal-entries` (+ post), Permission/audit, contracts + gateway
G319 tests. OpenAPI must not expose period-close, FX revaluation, bank recon,
bridges, or Brain/Twin surfaces on this slice.

## Out

GL2 period/close, GL3 bridges, GL4 FX revaluation, GL5 bank recon, tax filing
network, Brain/Twin, AP*, RET*, F3.

## Prerequisites

- TRACK-TAX3 COMPLETE; Alembic tip `0052_finance_tax_rate_authority_port_g317`
- Post-CRM queue; finance shell patterns (Tax1/F1)

## Product Owner response

**Approve — 2026-07-26 explicit “GL1（PHX-G319 / 0053）” authorization.**  
Milestone: **PHX-G319**. Auto-stop at TRACK-GL1 COMPLETE; await GL2.
