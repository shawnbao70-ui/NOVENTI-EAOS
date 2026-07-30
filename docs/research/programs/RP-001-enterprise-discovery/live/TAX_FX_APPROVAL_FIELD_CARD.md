# RP-001 Tax / FX / Approval Field Card

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, dossier, and HOLD how discovery cohorts encounter **税票 · FX · 审批** field boundaries—**税票主账缺席**, **AR vs 打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18 Human Confirm**, and **GET 审批/confirm**—through Sense→Structure→Score→Dossier. Knowledge labels (tax-invoice-deepen, fx-revaluation-deepen, approval-center-deepen) remain **hypotheses** for field mapping; do **not** edit `docs/knowledge/**`.

## Tax / FX / approval observation points (RP-001 lens)

1. **税票主账缺席 in discovery language:** whether facilitators treat Post AR, NDE “Invoice,” or printable PDF as a sales tax-invoice master during Structure/Score.
2. **AR ≠ 打印 ≠ 税票:** separate DO Post AR accrual, NDE/print commercial invoice, and any claimed tax-invoice authority in cohort vocabulary and demos.
3. **FX snapshot vs propagation:** note currency/rate fields shown on Quote vs whether Convert/SO/Receipt/AR carry dated FX (hypothesis: often absent).
4. **无重估 / 无汇兑损益:** capture whether discovery dossiers invent period revaluation or realized FX as “observed capability.”
5. **V18 vs Approval Center:** distinguish local Human Confirm / Type A gates from Approval Center records in discovery tooling.
6. **GET confirm / GET approve:** flag confirmation or approval-looking paths reachable via GET, prefetch, or replayable link.
7. **Score ≠ tax/FX/approval grant:** discovery scores and readiness labels must not appear as tax filing, FX policy, or approval authority.
8. **Brain/Twin fence:** HOLD any Brain recommendation or Twin state presented as tax release, FX revalue, or authorize.

## Scoring / HOLD

- Score entity presence (税票主账), surface separation (AR / print / tax), FX lineage (snapshot vs propagate vs revalue), and approval locus (V18 vs center) plus method integrity (GET vs POST).
- Dossier “not observed,” “UI-only,” and “server-enforced” separately; label knowledge extracts as hypotheses.
- HOLD whenever facilitator narrative or paper deepen is the only tax/FX/approval evidence.

## Required live evidence

1. Authorized, dated/tokenized map of AR Post, print/NDE invoice, and any tax-invoice entity (or attested absence) in the discovery cohort context.
2. Redacted Quote→Convert→SO→Receipt/AR extracts showing currency/FX fields present or absent at each hop.
3. Evidence of revaluation job / unrealized-realized FX (or custodian-attested absence) with `as_of`.
4. Method/route evidence for confirm/approve surfaces (GET vs POST), plus V18 vs Approval Center locus map.
5. Custodian corroboration separating print success from tax-invoice lifecycle and from approval authority.
6. Custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-001 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Kernel/API/UI, route, tax/FX schema, or product-code change.
3. No Brain execute, Twin authorize, product CRUD, Post AR / print-as-tax, Convert/Approve/Receive action, or FX revalue execution.
4. No synthetic/demo tax-invoice, FX, or approval artifact relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no tax filing, FX posting, approval, convert, confirm probe, or remediation.
