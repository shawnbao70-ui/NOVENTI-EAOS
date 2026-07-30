# RP-002 Tax / FX / Approval Field Card

**Program:** Enterprise DNA  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD whether **税票 · FX · 审批** behaviors are **stable enterprise invariants** or local variants: **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, and **GET 审批**. Knowledge deepen conclusions are hypotheses only; do **not** edit `docs/knowledge/**` or declare DNA from paper extracts.

## Tax / FX / approval observation points (RP-002 lens)

1. **Tax-invoice DNA candidate:** compare whether any site maintains a sales tax-invoice master vs relying on AR/print aliases.
2. **AR/print separation invariance:** test if “Invoice” vocabulary collapses print and Post AR into one DNA rule across contexts.
3. **FX propagation DNA:** check Quote/PO currency-rate columns vs Convert/SO/AR/AP for consistent propagation or consistent absence.
4. **Revaluation absence as (non-)invariant:** record whether period revaluation / FX P&L is universally missing or locally invented outside system.
5. **Approval locus drift:** V18 Human Confirm vs Approval Center participation as site-local vs claimed enterprise DNA.
6. **GET approve method DNA:** whether GET mutation on confirm/approve is residual-route drift or a repeated pattern.
7. **Alias labels:** tax invoice / commercial invoice / AR invoice / NDE invoice vocabulary with different runtime effects.
8. **Brain/Twin non-DNA:** HOLD claims that AI recommendation constitutes tax, FX, or approval enterprise DNA.

## Scoring / HOLD

- Score consistency across ≥2 contexts, provenance, method integrity, and stage separation (print vs AR vs tax; snapshot vs revalue; confirm vs center).
- Dossier each variant; do not collapse conflicting tax/FX/approval behaviors into one DNA rule.
- HOLD when a single site’s print PDF or V18 confirm is presented as enterprise-wide tax or approval DNA.

## Required live evidence

1. Authorized policy/config/schema snapshots of tax-invoice vs AR vs print from ≥2 relevant contexts.
2. Cross-context Quote→downstream extracts proving FX propagate or documenting non-propagation.
3. Revaluation / FX clearing artifacts or documented absence with owner across compared contexts.
4. Route/method inventory for confirm/approve including GET candidates; V18 vs Approval Center comparison.
5. Policy-version and residual/canonical route comparison for invoice and approval surfaces.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-002 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, policy store, Identity, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, tax/FX posting, approve/convert probe, or impersonation.
4. No synthetic multi-site comparison relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It defines no enterprise tax/FX/approval DNA and authorizes no gate or schema change.
