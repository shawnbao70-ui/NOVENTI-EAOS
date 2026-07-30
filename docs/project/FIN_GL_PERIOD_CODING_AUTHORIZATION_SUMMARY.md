# Coding Authorization Summary — Finance GL Period + Close (GL2)

## Milestone

**PHX-G320** — GL2, following PHX-G319 / GL1.

## Alembic

**`0054_finance_gl_period_g320`** revising
`0053_finance_gl_chart_journal_g319`.

## Authorized

Package `noventi.finance`: tenant-scoped accounting period (`GlPeriod`) with
lifecycle `open → closed` (irreversible close), bind journal entries to a period,
block `post` into closed periods, Alembic `0054`, gateway
`/v1/finance/gl-periods` (+ close), Permission/audit, contracts + gateway G320
tests. OpenAPI must not expose bridges, FX revaluation, bank recon, or
Brain/Twin on this slice.

## Out

GL3 bridges, GL4 FX, GL5 bank recon, soft-reopen, multi-book, Brain/Twin.

## Prerequisites

- TRACK-GL1 COMPLETE; tip `0053_finance_gl_chart_journal_g319`
- ADR-0351 GL chart/journal boundary

## Product Owner response

**Approve — 2026-07-26 explicit “GL2（PHX-G320 / 0054）” authorization.**  
Milestone: **PHX-G320**. Auto-stop at TRACK-GL2 COMPLETE; await GL3.
