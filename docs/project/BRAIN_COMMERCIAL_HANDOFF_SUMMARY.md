# Brain Commercial Handoff Summary

**Milestone:** PHX-G339  
**Track:** TRACK-BRAIN-COMMERCIAL-HANDOFF COMPLETE  
**Alembic:** none — tip remains `0067_finance_gl_ap_bridges_g338`

## Delivered

- Added the explicit `POST /v1/platform/commercial-handoffs/rma-credit-note`
  orchestrator. It requires `pkg.platform.commercial_handoff` /
  `handoff_rma_credit_note`, exactly one Brain insight or Twin snapshot source,
  and `human_confirm: true`.
- The orchestrator first obtains the existing G335 authorization, then calls
  only `CRMService.create_credit_note_from_return_authorization` to create or
  return a draft credit note for a restocked RMA.
- The handoff is audited as `Platform.CommercialHandoff.RmaCreditNote` with
  source, RMA, credit note, and idempotency evidence. G335 stays non-writing,
  and Z3 remains advisory with `execution_authority: none`.

## Verification

`18 passed`:
G339 handoff contracts plus G335 HTTP/service and G337 CRM credit-note
regressions.
