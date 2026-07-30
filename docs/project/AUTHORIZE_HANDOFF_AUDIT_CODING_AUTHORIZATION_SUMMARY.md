# Coding Authorization Summary — Authorize↔Handoff Audit Link (G392)

## Milestone

**PHX-G392** — correlate G335 authorize/execute audit_id into handoff records.

## Alembic

**none** — tip remains `0092_finance_realized_fx_gl_bridge_g372`.

## Authorized

1. Persist `authorization_audit_id` on handoff ok audit details and response
   (`SoConfirm` and `RmaCreditNote`).
2. Contracts proving handoff `authorization_audit_id` equals
   `Brain.RequestExecution` / `Twin.AuthorizeFromTwin` audit id and differs
   from handoff audit id.

## Out

Baseline (G393), Marketplace PSP, silent commercial writes.

## Product Owner response

**Approve — Batch-B; auto-continue G393 FINAL STOP.**
