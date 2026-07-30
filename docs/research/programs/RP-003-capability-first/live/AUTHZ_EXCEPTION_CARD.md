# RP-003 Authorization Exception Card

**Program:** Capability First  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD whether authorization follows a stable capability boundary rather than menu placement or route ownership. No capability, permission, or command is opened by this research card.

## Authorization / bypass observation points

1. Map each sampled intent to UI action, endpoint, service command, capability, and owning policy.
2. Compare create, view, edit, approve, convert, ship, post, reopen, and reconcile permission granularity.
3. Observe capability checks on canonical, residual, alias, integration, and batch paths.
4. Trace object, tenant, site, owner, state, amount, and segregation-of-duty constraints beyond module permission.
5. Record administrator, emergency, service-account, or support bypasses around capability checks.
6. Compare UI visibility and confirmation gates with server-side command authorization.
7. Observe whether denial is side-effect free and produces a reviewable decision record.

## Scoring / HOLD

- Score intent-to-capability fit, enforcement coverage, contextual scope, denial integrity, and override governance.
- Dossier duplicate or mismatched capabilities instead of choosing a preferred authority.
- HOLD any candidate capability inferred only from route names, buttons, or successful writes.

## Required live evidence

1. Authorized intent-to-surface-to-policy mapping for sampled commands.
2. Redacted allow/deny traces across canonical and alternate paths.
3. Context-constraint evidence for tenant, object, owner, state, and segregation of duties.
4. Privileged/service-account override records and review controls.
5. Denial, audit, retry, and no-side-effect evidence.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-003 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, capability mint, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, permission catalog, Kernel/API/UI, or product-code change.
3. No Brain execute, Twin authorize, CRUD, direct endpoint invocation, role change, or bypass.
4. No synthetic capability map relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no capability, command, permission, or implementation.
