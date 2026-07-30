# RP-008 Tax / FX / Approval Field Card

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [APPROVAL_BOUNDARY_CARD](APPROVAL_BOUNDARY_CARD.md) · [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD **plant / warehouse / quality** intersections with **税票 · FX · 审批**—Ship/Receive/Post AR/print must not be treated as tax-invoice masters; plant FX displays must not imply revaluation; V18 Approve/Receive gates must stay distinct from Approval Center. Themes: **税票主账缺席**, **AR/打印分离**, **FX 不传播 / 无重估**, **Approval Center vs V18**, **GET 审批**. Observation must not command OT. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Tax / FX / approval observation points (RP-008 lens)

1. **DO Invoice / Post AR ≠ 税票:** plant Invoice actions that create `ar_records` without tax-invoice entity.
2. **Warehouse print ≠ tax filing:** NDE/commercial print at kiosk/shared terminal separated from statutory tax invoice.
3. **Ship Complete ≠ tax-invoiced value:** unshipped/duplicate warnings vs tax-invoice lifecycle (hypothesis: absent).
4. **PO currency vs receive:** PO FX/rate fields that do not propagate into receive/AP/plant valuation.
5. **No plant revaluation:** inventory/AR plant reports must not be scored as FX period revaluation.
6. **PO Approve / Human Confirm vs Receive vs Approval Center:** local V18 gates vs center; Approve ≠ Receive eligibility.
7. **GET confirm/receive/approve on shared terminals:** mutation via GET under shared login or shift handover.
8. **Brain/Twin / OT fence:** no Brain execute, Twin authorize, or device command from tax/FX/approval-looking UI.

## Scoring / HOLD

- Score IT/OT locus, principal/device identity, AR/print/tax separation, FX lineage, and approve vs receive vs ship stages.
- Dossier plant and finance facts separately including clocks and custody.
- HOLD when physical presence, HMI visibility, or print success is treated as tax invoice or Approval Center decision.

## Required live evidence

1. Authorized redacted plant/warehouse map of Post AR, print/NDE, and any tax-invoice surface (or attested absence).
2. Before/after Ship/Receive/Post AR states showing no tax-invoice master created (or documenting if created).
3. PO→receive/AP currency-rate extracts proving propagate or non-propagate; revaluation absence attestation.
4. V18 Approve/Receive vs Approval Center locus evidence; GET vs POST inventory on confirm/receive/approve paths.
5. Shared-terminal / shift-handover attribution for any confirm/approve/print action.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers; no OT command issuance.

Missing evidence keeps RP-008 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, MES/WMS/OT config, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, receive/ship/adjust, Post AR, tax/FX posting, device command, or approve execution.
4. No synthetic plant walkthrough relabeled as live tax/FX/approval evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no plant, inventory, tax, FX, or approval action.
