# RP-009 Authorization Exception Card

**Program:** Enterprise Brain Evolution  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD the boundary between analysis, recommendation, approval, delegation, and execution. Brain-labelled metadata or output never constitutes command authority.

## Authorization / bypass observation points

1. Distinguish read, analyze, recommend, draft, approve, authorize, execute, and reconcile stages.
2. Observe which human or service principal owns each stage and whether identity remains attributable.
3. Trace data, tenant, object, action, amount, state, time, and tool scope for recommendations and commands.
4. Record Admin, operator, emergency, service-account, delegated, or “act as” bypass paths.
5. Compare confidence, explanation, task assignment, and UI approval labels with server authorization.
6. Observe stale recommendation, replay, duplicate execution, changed-state, revocation, and re-approval handling.
7. Capture denial, escalation, override reason, audit correlation, and unchanged business facts.

## Scoring / HOLD

- Score separation of duties, principal continuity, scope, freshness, explicit approval, and audit causality.
- Dossier recommendations separately from decisions and business writes.
- HOLD whenever inference quality, AI metadata, or an approval-looking surface is presented as execution authority.

## Required live evidence

1. Authorized redacted stage-and-principal map from input through any downstream decision.
2. Existing allow/deny decision traces showing explicit human/service authorization boundaries.
3. Scope, freshness, policy/model version, revocation, and re-approval artifacts.
4. Privileged/delegated/service-account exception records with expiry and review.
5. Audit correlation and no-side-effect evidence distinguishing recommendation from execution.
6. Custodian corroboration, consent/minimization, custody, retention, contradictions, and falsifiers.

Missing evidence keeps RP-009 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, Brain opening, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, Brain/Twin/Identity, model, tool, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, CRUD, recommendation execution, credential use, impersonation, or bypass.
4. No synthetic AI decision trace relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It grants no Brain, model, agent, human, tool, or execution authority.
