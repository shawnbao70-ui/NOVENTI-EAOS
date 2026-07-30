# RP-005 Tax / FX / Approval Field Card

**Program:** AI Workforce Transformation  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD how **AI workforce / AI Employee** surfaces interact with **税票 · FX · 审批** boundaries—especially that task/registry metadata ≠ tax release, FX revalue, or Approval Center authority. Field themes: **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, **GET 审批**. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`. Role/Title/Capability ≠ grant.

## Tax / FX / approval observation points (RP-005 lens)

1. **AI task “invoice” ≠ 税票主账:** workforce tasks labeled invoice/print that do not create a tax-invoice entity.
2. **Agent-assisted print vs AR Post:** AI-guided NDE/print success must stay separated from Post AR and from tax filing.
3. **AI rate suggestion ≠ FX authority:** recommended exchange rates without dated FX source, Convert propagation, or revaluation job.
4. **AI Employee ≠ Approval Center approver:** registry/task assignee presented as multi-step approval principal.
5. **V18 Human Confirm vs AI click-through:** human-in-loop confirm must remain distinguishable from agent auto-advance.
6. **GET approve by agent/tooling:** prefetch or tool-calling GET that mutates approve/reject state.
7. **auto_grant_minted: never:** tax/FX/approval-looking AI outcomes must not mint grants or filing rights.
8. **Brain execute / Twin authorize fence:** AI Employee ≠ Brain execute; Twin state ≠ tax/FX/approval authority.

## Scoring / HOLD

- Score human vs agent locus, principal attribution, method integrity, and stage separation (task vs print vs AR vs tax; suggest vs revalue; confirm vs center).
- Dossier AI assistance as non-authority unless live artifacts prove otherwise.
- HOLD when workforce metrics or task completion are treated as tax/FX/approval Completes.

## Required live evidence

1. Authorized redacted AI task/registry records referencing invoice/tax/FX/approve with linked business objects.
2. Before/after states proving agent/print/task did not create tax-invoice master (or documenting if it did).
3. FX suggestion vs Convert/SO/AR field evidence; revaluation absence or presence with `as_of`.
4. Named human approver artifacts for V18 and/or Approval Center; GET vs POST method notes on agent-touched paths.
5. Attestation that Role/Title/Capability/AI task completion did not mint grants (`auto_grant_minted: never` posture held).
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-005 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, workforce registry rewrite, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, Cap→grant, tax/FX posting, or approve/reject execution by agent or human-on-behalf without separate authority.
4. No synthetic AI walkthrough relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no AI execution, grant mint, tax, FX, or approval action.
