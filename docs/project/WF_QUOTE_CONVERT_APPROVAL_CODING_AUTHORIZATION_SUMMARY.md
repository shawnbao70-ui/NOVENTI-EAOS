# Coding Authorization Summary — Workflow Approval Quote.convert (G353)

## Milestone

**PHX-G353** — ADR-0318; **unique command: Quote.convert only**.

## Alembic

**`0077_crm_quote_convert_approval_g353`** (policy column) revising `0076_…`,
or none if reusable JSON/policy row — prefer column on TenantConfirmPolicy.

## Authorized

Mirror G348: tenant `quote_convert_approval_required`; gate action
`crm.quote.convert`; convert blocked until Workflow approved; approve ≠ auto
convert; human_confirm + Permission unchanged when policy on.

## Out

DO.ship wiring (G354), Unship, commission.

## Product Owner response

**Approve — batch; auto-continue G354.**
