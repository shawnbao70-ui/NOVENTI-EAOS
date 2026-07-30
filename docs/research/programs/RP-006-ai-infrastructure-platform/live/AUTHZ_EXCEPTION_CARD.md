# RP-006 Authorization Exception Card

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md) · [DUAL_WRITE_FIELD_CARD](DUAL_WRITE_FIELD_CARD.md) · [NUMBERING_CUSTODY_CARD](NUMBERING_CUSTODY_CARD.md)

## Field objective

Observe, score, and HOLD authorization enforcement across platform, API, route, middleware, service, integration, and tenant boundaries. Registered or mounted surfaces are not proof of secure runtime capability.

## Authorization / bypass observation points

1. Map authentication, CSRF, RBAC, tenant, object, and state enforcement loci for sampled routes.
2. Compare canonical, residual, alias, versioned API, integration, and administrative surfaces.
3. Observe whether mutating GET, replay, stale token, duplicate request, and prefetch controls are explicit.
4. Trace platform-admin, operator, service-account, break-glass, and support bypass boundaries.
5. Compare UI/menu visibility with API and service authorization for the same intent.
6. Observe default tenant, cross-tenant identifier, owner scope, and direct-object access handling.
7. Capture policy/config version, decision logs, denial response, alerting, and unchanged-state evidence.

## Scoring / HOLD

- Score enforcement coverage, layer consistency, tenant isolation, replay resistance, override custody, and observability.
- Dossier every route owner and deployment variant; do not infer global middleware from selected endpoints.
- HOLD when route registration, health output, or UI hiding is the only security evidence.

## Required live evidence

1. Authorized route/middleware/service enforcement map with deployment and policy versions.
2. Redacted allow/deny traces across canonical and alternate surfaces.
3. Tenant/object/owner scope and cross-tenant denial evidence.
4. Service/admin/break-glass exception lifecycle and audit artifacts.
5. Method, CSRF, token, replay/idempotency, alert, and no-side-effect evidence.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-006 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, infrastructure opening, or Eng ingest.
2. No Const/BP, `docs/knowledge/**`, middleware, route, Identity, Kernel/API/UI, platform config, or code change.
3. No Brain execute, Twin authorize, CRUD, API probe, token use, tenant crossover, or bypass execution.
4. No synthetic platform-security result relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no platform access, security test, configuration, or remediation.
