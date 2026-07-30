# Coding Authorization Summary — Finance GL FX Revaluation (GL4)

## Milestone

**PHX-G322** — GL4, following PHX-G321 / GL3.

## Alembic

**`0056_finance_gl_fx_revaluation_g322`** revising `0055_finance_gl_bridges_g321`.

## Authorized

Package `noventi.finance`: period-bound FX revaluation shell that produces a
balanced JournalEntry for an open GlPeriod; fail-closed FX rate port
(RejectAll default + Fake for tests); no live market feed; HTTP under
`/v1/finance/gl-fx-revaluations` (or equivalent); contracts + gateway G322.

## Out

GL5 bank recon, live FX network, Brain/Twin, multi-book.

## Product Owner response

**Approve — 2026-07-26 batch “GL 收尾串行” includes GL4.**  
Auto-continue to GL5 after TRACK-GL4 COMPLETE.
