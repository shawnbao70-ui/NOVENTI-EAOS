# RP-005 Authorization Exception Card

**Program:** AI Workforce Transformation  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD authorization exceptions involving humans, service identities, automation, and AI-labelled workforce records. Metadata, recommendations, and task assignment do not prove controlled execution.

## Authorization / bypass observation points

1. Distinguish human principals, service accounts, bots, AI-labelled employees, and delegated sessions.
2. Observe whether proposed actions require a fresh human authorization at the command boundary.
3. Trace tool, data, tenant, object, amount, state, and time limits attached to non-human identities.
4. Record Admin, operator, service-account, emergency, and “act as” bypasses plus their expiry and review.
5. Compare task assignment, approval labels, browser prompts, and UI visibility with server enforcement.
6. Observe credential custody, rotation, revocation, joiner/mover/leaver, and orphaned-agent handling.
7. Capture denial, escalation, override, audit actor, and rollback evidence for high-impact intents.

## Scoring / HOLD

- Score principal clarity, delegation chain, least privilege, human gate, credential custody, and audit attribution.
- Dossier recommendations and metadata separately from attempted or completed actions.
- HOLD whenever an AI label, task record, or service credential is presented as execution authority.

## Required live evidence

1. Authorized principal inventory distinguishing human and non-human identities.
2. Redacted decision traces showing delegation and human authorization for sampled high-impact intents.
3. Tool/data/object/tenant/time/amount scope and policy-version artifacts.
4. Credential issue, rotation, revocation, expiry, and privileged override records.
5. Denial, escalation, audit actor, and no-side-effect/rollback evidence.
6. Custodian corroboration, consent/minimization, custody, retention, contradictions, and falsifiers.

Missing evidence keeps RP-005 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, Identity/Brain/Twin, Kernel/API/UI, agent, or product-code change.
3. No Brain execute, Twin authorize, CRUD, tool invocation, credential use, impersonation, or privilege escalation.
4. No synthetic AI-workforce trace relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It grants no human, AI, agent, bot, service, or tool authority.
