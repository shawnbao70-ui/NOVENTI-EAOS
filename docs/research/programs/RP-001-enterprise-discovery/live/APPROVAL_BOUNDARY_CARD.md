# RP-001 Approval Boundary Card

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, dossier, and HOLD how discovery cohorts encounter **approval boundaries**—local **V18 Human Confirm** versus **Approval Center**, **Approve ≠ Convert**, **GET confirm**/mutation surfaces, missing multi-step approval, and Brain/Twin non-authority—without treating the read-only knowledge package as live fact. Knowledge labels (V18, Human Confirm, Approval Center) remain **hypotheses** for field mapping; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **V18 vs Approval Center:** distinguish local Human Confirm / business-gate confirmation from centralized Approval Center records during Sense→Structure→Score→Dossier.
2. **Approve ≠ Convert:** observe whether a discovery “approve/confirm” gesture is conflated with Convert or other commercial mutations in facilitator language or UI labels.
3. **GET confirm:** note any confirmation or state-changing path reachable via GET, prefetch, or replayable link in discovery tooling or adjacent commercial demos.
4. **Multi-step missing:** capture whether named approver, Pending→Approved sequence, segregation of duties, and re-approval after change are absent or only documentary.
5. **UI confirm ≠ authz:** compare browser/Human Confirm prompts with independent server permission and object-scope checks (map to AUTHZ_EXCEPTION_CARD).
6. **Score ≠ grant:** ensure discovery scores, readiness labels, and dossier advice never appear as permission, approval, or grant evidence.
7. **Brain/Twin fence:** record any Brain recommendation or Twin twinning language presented as approve/authorize/execute during discovery; HOLD as non-authority.

## Scoring / HOLD

- Score locus (local V18 vs center), method (POST vs GET), stage separation (confirm vs convert vs authorize), multi-step completeness, and Brain/Twin non-authority.
- Dossier “not observed,” “UI-only,” and “server-enforced” separately.
- HOLD whenever facilitator narrative or knowledge extract is the only approval-boundary evidence.

## Required live evidence

1. Authorized, dated/tokenized map of confirmation vs Approval Center vs Convert surfaces in the discovery cohort context.
2. Redacted before/after states showing Approve/confirm did not imply Convert (or documenting when it did).
3. Method/route evidence for confirm paths (GET vs POST), plus anti-replay/CSRF posture or documented absence.
4. Multi-step approval artifacts (named approver, Pending, decision, re-approval) or attested absence.
5. Custodian corroboration separating Human Confirm intent from RBAC/authorization decisions.
6. Custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-001 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Kernel/API/UI, route, or product-code change.
3. No Brain execute, Twin authorize, product CRUD, Convert/Approve/Receive action, or acceptance-on-behalf.
4. No synthetic/demo confirmation relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no approval, convert, confirm probe, or remediation.
