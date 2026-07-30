# RP-002 Authorization Exception Card

**Program:** Enterprise DNA  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD whether authorization behavior is a stable enterprise invariant or a collection of local exceptions. Capture policy lineage and variation without exercising bypasses or changing any authority.

## Authorization / bypass observation points

1. Compare the same business intent across UI, route, service, API, integration, and batch surfaces.
2. Observe whether role/module/action names have one definition or aliases with different effects.
3. Trace tenant, owner, business-unit, and record-scope checks across equivalent commands.
4. Record privileged-role short circuits and whether local teams add undocumented exemptions.
5. Compare Human Confirm, approval status, and browser prompts with actual server authorization.
6. Observe policy-version drift between sites, deployments, residual routes, and canonical routes.
7. Capture denial, override, expiry, review, and audit semantics as candidate enterprise invariants.

## Scoring / HOLD

- Score consistency, policy provenance, scope completeness, exception explicitness, and auditability.
- Dossier each variant; do not normalize conflicting policies into one “DNA” rule.
- HOLD when a local role name or UI behavior is presented as an enterprise-wide authorization invariant.

## Required live evidence

1. Authorized policy/configuration snapshots from at least two relevant surfaces or contexts.
2. Redacted allow/deny traces tied to principal, role, tenant, object, action, and policy version.
3. Alias, residual/canonical route, or deployment-variation evidence.
4. Privileged bypass and exception lifecycle artifacts, including owner and review.
5. Denial immutability and audit/event evidence for comparable commands.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-002 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, policy store, Identity, Kernel/API/UI, or code modification.
3. No Brain execute, Twin authorize, CRUD, role grant, impersonation, direct-route test, or bypass execution.
4. No synthetic policy comparison relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It defines no enterprise authorization DNA and authorizes no policy change.
