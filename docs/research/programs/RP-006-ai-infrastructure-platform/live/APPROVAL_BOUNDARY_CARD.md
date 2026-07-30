# RP-006 Approval Boundary Card

**Program:** AI Infrastructure Platform  
**Status:** **Open** · **0 Complete**  
**Live context / observer:** not supplied / not supplied  
**Related:** [AUTHZ_EXCEPTION_CARD](AUTHZ_EXCEPTION_CARD.md) · [EXCEPTION_PATH_CARD](EXCEPTION_PATH_CARD.md)

## Theme and knowledge mapping

Observe, score, and HOLD approval-boundary enforcement across **platform, API, middleware, route, and tenant layers**: **V18 Human Confirm** vs **Approval Center**, **Approve ≠ Convert**, **GET confirm**/mutation, missing multi-step checks, and Brain/Twin non-authority. Route registration ≠ secure approval gate. Knowledge remains hypothesis-only; do **not** edit `docs/knowledge/**`.

## Approval boundary observation points

1. **Layer locus:** map where Human Confirm and Approval Center are enforced (template, router, service, middleware) vs UI-only.
2. **GET confirm surface:** inventory mutating GET confirm/approve/receive-adjacent paths and CSRF/prefetch/replay controls.
3. **Approve≠Convert at API:** compare POST Type A approve with convert/create DO endpoints for independent gates.
4. **Approval Center API holes:** decision endpoints missing Pending integrity, approver binding, or approve permission.
5. **Tenant/object scope on confirm:** whether confirm/approve ignores tenant/owner scope at platform boundary.
6. **Multi-step platform support:** absence of workflow engine steps does not invent Approval Center completeness.
7. **Brain/Twin platform fence:** platform tooling must not treat model/tool invocation as approve/authorize/execute.

## Scoring / HOLD

- Score enforcement coverage, method integrity, layer consistency, tenant isolation, and observability of decisions.
- Dossier every route owner/deployment variant; do not infer global middleware from selected endpoints.
- HOLD when route mount, health, or UI hiding is the only approval-boundary evidence.

## Required live evidence

1. Authorized route/middleware map for confirm, Approval Center, approve, and convert surfaces.
2. Method evidence (GET vs POST) with anti-replay/CSRF posture or documented absence.
3. Redacted allow/deny traces proving Approve≠Convert at service layer.
4. Approval Center decision artifacts with policy/version and principal checks or attested gaps.
5. Tenant/object-scope denial and unchanged-state evidence.
6. Custodian corroboration, custody, minimization, retention, contradictions, and falsifiers.

Missing evidence keeps RP-006 **Open / 0 Complete**.

## HARD HOLD

1. No Promote, floor flip, Complete registration, or Eng soft-queue ingest.
2. No Const/BP, `docs/knowledge/**`, platform Identity, Kernel/API/UI, middleware, or code change.
3. No Brain execute, Twin authorize, product CRUD, direct-route probe, or approve/convert execution.
4. No synthetic platform security scan relabeled as live evidence.

## Non-claim

This card **≠ Complete** and **≠ Eng soft-queue ingest**. It authorizes no platform, route, approval, or security change.
