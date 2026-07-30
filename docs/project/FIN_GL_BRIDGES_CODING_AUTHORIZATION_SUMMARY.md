# Coding Authorization Summary — Finance GL Bridges (GL3)

## Milestone

**PHX-G321** — GL3, following PHX-G320 / GL2.

## Alembic

**`0055_finance_gl_bridges_g321`** revising `0054_finance_gl_period_g320`.

## Authorized

Package `noventi.finance`: idempotent bridges from existing finance facts
(AR invoice issued, AR receipt applied, tax invoice issued, commission accrued)
into draft/posted JournalEntry under an open GlPeriod; tenant mapping of
source→GL accounts (minimal bridge policy or account-role map); Permission/audit;
HTTP under `/v1/finance/gl-bridges` (or equivalent); contracts + gateway G321.
No Brain/Twin; no AP/RET/F3.

## Out

GL4 FX, GL5 bank recon, live network, automatic multi-book, Brain/Twin.

## Product Owner response

**Approve — 2026-07-26 batch “GL 收尾串行” includes GL3.**  
Auto-continue to GL4 after TRACK-GL3 COMPLETE.
