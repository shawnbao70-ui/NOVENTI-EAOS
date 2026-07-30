# RP-009 Approval Boundary Card

**Program:** Enterprise Brain Evolution  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD the boundary between **analyze / recommend / draft / Human Confirm / Approval Center / approve / authorize / execute**. Brain-labelled output never constitutes command authority. Map **V18 Human Confirm** vs **Approval Center**, **Approve ≠ Convert**, **GET confirm**, missing multi-step human gates, and **Brain execute / Twin authorize** hard fences. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **Stage separation:** distinguish recommendation, Human Confirm intent, Approval Center decision, Convert/execute, and Twin authorize (closed).
2. **V18 vs center for AI drafts:** AI-drafted docs still require independent local confirm and/or center decision—observe which, if either.
3. **Approve≠Convert after Brain suggest:** suggestion acceptance ≠ Convert; Convert needs its own gate.
4. **GET confirm on AI deep links:** stale recommendation links that GET-mutate or confirm without fresh principal.
5. **Multi-step re-approval:** material change after Brain recommendation requires Pending reset / re-approval—observe absence.
6. **Confidence ≠ approval:** UI confidence, explanation, or “AI approved” labels vs server authorization.
7. **Brain/Twin absolute fence:** Brain execute and Twin authorize remain closed; dossier any path that collapses recommend→authorize→execute.

## Scoring / HOLD

- Score separation of duties, principal continuity, freshness, explicit human approval, and audit causality.
- Dossier recommendations separately from Approval Center decisions and business writes.
- HOLD whenever inference quality or an approval-looking AI surface is presented as execution authority.

## Required live evidence

1. Authorized redacted stage-and-principal map from Brain input through any human confirm/Approval Center/decision.
2. Existing allow/deny traces showing explicit human gates independent of model output.
3. Approve≠Convert evidence on AI-assisted commercial paths.
4. Freshness, revocation, re-approval, and stale-link (GET) handling artifacts.
5. Audit correlation proving no Brain execute / Twin authorize side effects from research observation.
6. Custodian corroboration, consent/minimization, custody, retention, contradictions, and falsifiers.

Missing evidence keeps RP-009 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, Brain opening, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Brain/Twin/Identity, model, tool, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, recommendation execution, credential use, or approve/convert action.
4. No synthetic AI decision/approval trace relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It grants no Brain, model, agent, human, Twin, or execution authority.
