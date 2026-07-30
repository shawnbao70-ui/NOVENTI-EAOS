# RP-007 Approval Boundary Card

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD approval-boundary **drift** during coexistence, rollout, rollback, and migration: **V18 Human Confirm** vs **Approval Center**, **Approve ≠ Convert**, **GET confirm** residual paths, missing multi-step gates on new surfaces, and Brain/Twin non-authority. This card records evolution hazards only; knowledge is hypothesis-only; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **Old/new confirm parity:** compare residual vs canonical routes for Human Confirm / Approval Center presence after a release.
2. **Approve≠Convert during cutover:** one path still couples approve to convert while the other separates them.
3. **GET confirm leftovers:** legacy GET mutation/confirm links remain reachable after POST Type A replacement.
4. **Center adoption lag:** UI shows Approval Center while server still relies on local V18 only (or inverse).
5. **Multi-step regression:** Pending/named-approver/re-approval lost or weakened across migration versions.
6. **Stale session confirm:** cached roles/sessions allowing confirm after policy rollback or entitlement change.
7. **Brain/Twin during evolution:** HOLD any migration narrative that uses Brain/Twin as temporary approve/authorize authority.

## Scoring / HOLD

- Score policy continuity, route parity, temporal scope, residual closure, and audit lineage across versions.
- Dossier each release context; do not average conflicting approval outcomes.
- HOLD when a migration plan or new UI is proof that legacy confirm/approve holes are closed.

## Required live evidence

1. Authorized before/after maps of confirm/Approval Center/approve/convert tied to release/config versions.
2. Residual GET confirm reachability evidence with timestamps.
3. Redacted state traces showing Approve≠Convert (or coupling) on old and new paths.
4. Multi-step approval artifacts across transition windows or attested regression.
5. Stale-session / rollback / break-glass confirm exception records.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-007 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, migration runbook execution, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, cutover action, or approve/convert probe.
4. No synthetic migration walkthrough relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no evolution, gate, or runtime change.
