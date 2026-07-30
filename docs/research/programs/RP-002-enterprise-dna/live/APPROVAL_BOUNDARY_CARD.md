# RP-002 Approval Boundary Card

**Program:** Enterprise DNA  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD whether approval boundaries are **stable enterprise invariants** or local variants: **V18 Human Confirm** vs **Approval Center**, **Approve ≠ Convert**, **GET confirm**, missing multi-step gates, and Brain/Twin non-authority. Knowledge conclusions are hypotheses only; do **not** edit `docs/knowledge/**` or declare DNA from paper extracts.

## Approval boundary observation points

1. **Invariant vs local V18:** compare the same business intent across sites for local Human Confirm gates versus Approval Center participation.
2. **Approve≠Convert DNA:** test whether “approved” status is treated as conversion eligibility across Quote/SO/DO-adjacent surfaces.
3. **GET confirm drift:** observe whether confirm/mutation method (GET vs POST) is consistent or varies by residual/canonical route.
4. **Alias labels:** capture approval vocabulary drift (Human Confirm, approve, authorized, signed) with different runtime effects.
5. **Multi-step completeness:** record presence/absence of named approver, Pending integrity, and re-approval after material change as DNA candidates.
6. **Policy-version lineage:** tie confirm/Approval Center behavior to deployment/config versions across contexts.
7. **Brain/Twin non-DNA:** HOLD any claim that AI recommendation or twin state constitutes an enterprise approval invariant.

## Scoring / HOLD

- Score consistency, provenance, method integrity, stage separation, and exception explicitness.
- Dossier each variant; do not collapse conflicting gates into one DNA rule.
- HOLD when a single site’s V18 confirm is presented as enterprise-wide approval DNA.

## Required live evidence

1. Authorized policy/config snapshots of confirm vs Approval Center from ≥2 relevant contexts.
2. Redacted allow/deny or state traces proving Approve≠Convert (or documenting coupling).
3. Route/method inventory for confirm surfaces including GET mutation candidates.
4. Multi-step approval lifecycle artifacts or documented absence with owner.
5. Policy-version and residual/canonical route comparison evidence.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-002 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, policy store, Identity, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, product CRUD, approve/convert probe, or impersonation.
4. No synthetic policy comparison relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It defines no enterprise approval DNA and authorizes no gate change.
