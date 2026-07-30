# RP-007 Authorization Exception Card

**Program:** Enterprise Evolution Engine  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD authorization drift during change, coexistence, rollout, rollback, and migration. This card records evolution hazards without changing policies, routes, roles, or runtime state.

## Authorization / bypass observation points

1. Compare old/new, canonical/residual, and versioned routes for equivalent command authorization.
2. Observe role, alias, tenant, object, and state-policy drift across release boundaries.
3. Trace migration, support, backfill, reconciliation, and break-glass identities with temporary privilege.
4. Record policy rollout order, cache/config propagation, stale sessions, and rollback behavior.
5. Compare UI release timing with server enforcement to expose visibility/enforcement gaps.
6. Observe whether legacy bypasses remain reachable after a replacement surface is introduced.
7. Capture denial, override, expiration, review, audit continuity, and unchanged-state evidence across transitions.

## Scoring / HOLD

- Score policy continuity, route parity, temporal scope, rollback safety, temporary privilege, and audit lineage.
- Dossier each version/context rather than averaging conflicting authorization outcomes.
- HOLD when a migration plan or new UI is used as proof that legacy bypasses are closed.

## Required live evidence

1. Authorized before/after route-policy maps tied to release/config versions and timestamps.
2. Redacted allow/deny traces for equivalent intents across coexistence surfaces.
3. Temporary migration/support/break-glass grant, expiry, review, and revocation artifacts.
4. Policy rollout, cache/session propagation, rollback, and residual-route evidence.
5. Continuous audit correlation and no-side-effect evidence for denials.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-007 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, migration authorization, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, policy, route, release, Kernel/API/UI, or code change.
3. No Brain execute, Twin authorize, CRUD, rollout, rollback, grant, direct-route test, or bypass.
4. No synthetic migration result relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no evolution, migration, policy rollout, or remediation.
