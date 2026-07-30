# RP-009 Tax / FX / Approval Field Card

**Program:** Enterprise Brain Evolution  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD **Brain / Twin** non-authority over **税票 · FX · 审批**—recommendations, scores, and twin mirrors must not create tax-invoice masters, propagate FX, run revaluation, or substitute for Approval Center / V18 Human Confirm. Themes: **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, **GET 审批**. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`. Brain execute / Twin authorize remain closed.

## Tax / FX / approval observation points (RP-009 lens)

1. **Brain “invoice advice” ≠ 税票主账:** recommendations that imply tax release without a tax-invoice entity.
2. **Twin mirror of AR/print ≠ tax identity:** twining commercial invoice/AR state must preserve AR≠print≠tax.
3. **Brain FX hint ≠ dated FX source:** exchange-risk scores or rate suggestions without Convert propagation or revaluation job.
4. **No Brain-triggered revaluation:** HOLD any narrative that Brain can post unrealized/realized FX.
5. **Brain recommend ≠ V18 confirm ≠ Approval Center:** three loci must stay distinguishable in UI and audit.
6. **GET approve via Brain tooling:** tool-calls or links that mutate approve/reject through GET.
7. **Twin authorize fence:** twin state must never be labeled authorize for tax filing, FX posting, or approval.
8. **Brain execute fence:** execute paths closed for tax/FX/approval mutations regardless of confidence scores.

## Scoring / HOLD

- Score recommendation vs authority, twin fidelity vs legal/tax identity, and fail-closed on Brain/Twin.
- Dossier every Brain/Twin mention of invoice/tax/FX/approve with non-authority default.
- HOLD Complete claims built only from Brain narratives or Twin dashboards.

## Required live evidence

1. Authorized redacted Brain/Twin outputs referencing invoice/tax/FX/approve with linked business objects (or attested none).
2. Evidence that Brain/Twin actions did not create tax-invoice, Post AR, print-as-tax, or FX journals.
3. Explicit non-execution / non-authorize controls for tax/FX/approval tool surfaces.
4. V18 vs Approval Center vs Brain-recommend locus map; GET vs POST method notes on Brain-touched paths.
5. Custodian corroboration that exchange-risk or invoice advice remained non-accounting / non-approval.
6. Custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-009 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Brain/Twin config, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, tax/FX posting, or approve/reject execution.
4. No synthetic Brain/Twin transcript relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no Brain execute, Twin authorize, tax, FX, or approval action.
