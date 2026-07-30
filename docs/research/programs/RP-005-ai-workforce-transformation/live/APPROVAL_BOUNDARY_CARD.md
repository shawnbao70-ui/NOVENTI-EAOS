# RP-005 Approval Boundary Card

**Program:** AI Workforce Transformation  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD approval boundaries when **humans, service identities, automation, and AI-labelled workforce** interact with **V18 Human Confirm**, **Approval Center**, **Approve ≠ Convert**, **GET confirm**, multi-step gaps, and Brain/Twin non-authority. Task assignment and AI metadata ≠ approval. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **Human Confirm principal:** who submits `human_confirm`—named human vs bot/service session—and whether audit attributes correctly.
2. **Approval Center vs AI task:** Approval Center decision ≠ AI task completion or recommendation acceptance.
3. **Approve≠Convert for agents:** automation that treats “approved” metadata as Convert/execute authority without fresh human gate.
4. **GET confirm automation:** scrapers, prefetch, or scheduled GETs that can fire confirm/mutation surfaces.
5. **Multi-step human gate:** absence of Pending→human Approve→re-approval after AI-proposed amount/state change.
6. **Credentialed confirm:** service accounts that can pass confirm without workforce SoD.
7. **Brain/Twin fence:** Brain execute / Twin authorize remain closed; dossier any UI that blurs recommend→approve→execute for AI workforce.

## Scoring / HOLD

- Score principal clarity, human gate freshness, stage separation, method integrity, and audit actor fidelity.
- Dossier recommendations and task records separately from approvals and business writes.
- HOLD whenever an AI label, task, or service credential is presented as approval authority.

## Required live evidence

1. Authorized principal inventory (human / service / AI-labelled) touching confirm and Approval Center.
2. Redacted decision traces showing fresh human authorization for high-impact intents.
3. Approve≠Convert evidence where automation or AI metadata is present.
4. GET confirm / replay controls or documented absence for automated clients.
5. Multi-step approval and re-approval artifacts after AI-proposed changes, or attested absence.
6. Custodian corroboration, consent/minimization, custody, retention, contradictions, and falsifiers.

Missing evidence keeps RP-005 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Identity/Brain/Twin, agent, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, tool invocation, credential use, or approve/convert execution.
4. No synthetic AI-workforce approval trace relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It grants no human, AI, agent, bot, or approval authority.
