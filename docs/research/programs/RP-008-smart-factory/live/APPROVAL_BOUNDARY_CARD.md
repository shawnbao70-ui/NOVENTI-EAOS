# RP-008 Approval Boundary Card

**Program:** Smart Factory  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD approval boundaries spanning **plant, warehouse, quality, receive/ship, and shared terminals**: **V18 Human Confirm** vs **Approval Center**, **Approve ≠ Convert/Receive/Ship**, **GET confirm**/receive surfaces, missing multi-step quality/ops gates, and Brain/Twin non-authority. Observation must not command OT/production. Knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **PO Approve vs Receive:** local V18 Approve / Human Confirm vs receive eligibility; Approval Center may be absent on receive chains (hypothesis for field check).
2. **Approve≠Convert/Ship:** plant workflows that treat approved commercial docs as automatic convert/ship authority.
3. **GET confirm/receive:** warehouse/kiosk GET links that mutate inventory or receive without POST confirm envelope.
4. **Quality disposition ≠ Approval Center Rejected:** map whether center reject is wrongly treated as material rejection (or ignored).
5. **Shared terminal Human Confirm:** shift handover / shared login confirming as wrong principal.
6. **Multi-step plant gates:** missing named approver / SoD between requester, quality, and inventory receiver.
7. **Brain/Twin / OT fence:** no Brain execute, Twin authorize, or device command from approval-looking UI.

## Scoring / HOLD

- Score IT/OT locus, principal/device identity, method integrity, stage separation (approve vs receive vs ship), and safe-state on denial.
- Dossier plant and enterprise facts separately including clocks and custody.
- HOLD when physical presence, HMI visibility, or shared terminal is treated as approval.

## Required live evidence

1. Authorized redacted map of approve/confirm/receive/ship gates at sampled plant/warehouse contexts.
2. Evidence that Approve≠Receive/Convert/Ship (or documenting illegal coupling) with before/after states.
3. GET vs POST method inventory for confirm/receive-adjacent surfaces.
4. Quality vs Approval Center disposition artifacts or attested non-linkage.
5. Shared-terminal / shift-handover confirm attribution evidence.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers; no OT command issuance.

Missing evidence keeps RP-008 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, MES/WMS/OT config, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, receive/ship/adjust, device command, or approve execution.
4. No synthetic plant walkthrough relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no plant, inventory, quality, or approval action.
