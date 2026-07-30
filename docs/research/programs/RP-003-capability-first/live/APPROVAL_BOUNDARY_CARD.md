# RP-003 Approval Boundary Card

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD whether approval boundaries follow **capability intent** rather than menu/button placement: map **V18 Human Confirm**, **Approval Center**, **Approve ≠ Convert**, **GET confirm**, multi-step gaps, and Brain/Twin non-authority to capability/command loci. Knowledge package mappings remain hypotheses; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **Intent→capability→confirm:** map each sampled approve/confirm/convert intent to capability, route, and gate type (V18 vs Approval Center).
2. **Approve≠Convert capability split:** verify create/edit/approve/convert permissions are distinct at the capability boundary, not collapsed by UI.
3. **GET confirm vs capability:** observe mutating GET confirm paths that bypass the expected capability+method envelope.
4. **Approval Center capability hole:** capture whether Approval Center decisions enforce approver identity, Pending state, and approve permission.
5. **Confirm ≠ RBAC:** Human Confirm records intent; score whether capability/RBAC still gates the same command independently.
6. **Multi-step capability:** identify missing segregation-of-duty or re-approval capabilities after amount/state change.
7. **Brain/Twin ≠ capability:** HOLD recommendations or twin outputs labelled “approve” that lack an explicit human capability grant.

## Scoring / HOLD

- Score intent-to-capability fit, gate locus, method integrity, stage separation, and denial without side effects.
- Dossier mismatched capabilities (UI approve vs server convert) without choosing a preferred model.
- HOLD any capability inferred only from button labels or successful writes.

## Required live evidence

1. Authorized intent-to-capability-to-gate map for approve/confirm/convert samples.
2. Redacted traces showing Approve≠Convert at capability and state layers.
3. Method/route evidence for GET confirm candidates and expected POST Type A paths.
4. Approval Center decision artifacts with principal/permission/Pending checks or attested gaps.
5. Denial/unchanged-state evidence when confirm or capability fails.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-003 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, capability registry, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, capability mint, or approve/convert execution.
4. No synthetic capability map relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It opens no capability, approval, or convert authority.
