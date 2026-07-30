# RP-001 Authorization Exception Card

**Program:** Enterprise Discovery  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Discover, score, dossier, and HOLD authorization exceptions without invoking them. Compare visible controls with server enforcement, actor scope, audit, and outcome; do not treat the read-only knowledge package as live fact.

## Authorization / bypass observation points

1. Compare hidden or disabled actions with direct-route authorization outcomes recorded by the site custodian.
2. Trace whether Convert, create DO, status change, receipt, approval, and reconciliation commands require an authenticated principal.
3. Observe module permission versus object owner, tenant, site, and record-scope enforcement.
4. Record Admin/Super Admin or emergency-role bypass boundaries, reason capture, expiry, and review.
5. Compare browser confirmation or Human Confirm with independent server-side permission checks.
6. Identify GET or replayable mutation paths and the controls against CSRF, prefetch, duplicate execution, and stale links.
7. Observe denial handling, including status code, unchanged facts, audit event, alert, and exception ownership.

## Scoring / HOLD

- Score principal identity, policy locus, object scope, decision trace, denial integrity, and override custody.
- Dossier “not observed,” “not permitted to test,” and “control absent” separately.
- HOLD whenever UI visibility, role labels, or a successful result is the only authorization evidence.

## Required live evidence

1. Authorized, dated/tokenized route/action inventory with UI and server policy mappings.
2. Redacted allow-and-deny decision traces for the same command and object class.
3. Principal, role, tenant/site, owner scope, and policy-version evidence.
4. Privileged or emergency override procedure plus real review/audit artifacts, or documented absence.
5. Mutation method, anti-replay/CSRF/idempotency, and unchanged-state evidence for denials.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-001 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, Kernel/API/UI, route, permission, or product-code change.
3. No Brain execute, Twin authorize, product CRUD, direct-route probe, privilege escalation, or acceptance-on-behalf.
4. No synthetic/demo authorization result relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no access attempt, bypass, mutation, or remediation.
