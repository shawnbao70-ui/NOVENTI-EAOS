# Decision Summary — Brain Execute + Twin Authorize Open

> Phoenix Gate Framework ([ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)).  
> Product Owner decision surface. **Design Gate Approved 2026-07-26.**

## Package

`eaos_platform.brain` + `eaos_platform.twin` — Execution open (governed)

## Purpose

Decide whether to lift the fail-closed ban on Brain `request_execution` and Twin
`authorize_from_twin`, under Permission + audit + narrow commercial handoff rules.

## Scope

Design + coding-auth decision only on this page. Z3 advisory read path stays;
this Summary does **not** revoke advisory.

## Architecture Boundary

- Kernel Permission Evaluate remains sole allow/deny for execute/authorize.
- Tenant fail-closed; no Cap→grant shortcut; no Legacy Admin bypass.
- Commercial writers (SO/DO/AR/Receipt/AP/RET/GL) must not silently call execute;
  any handoff must be explicit, audited, and Permission-gated.
- Advisory `execution_authority: "none"` remains true for Z3 GET envelopes
  unless a separate Amend changes advisory semantics.

## In Scope

- Allow `POST /v1/brain/insights/{id}/execute` to succeed when Permission allows
  and insight is eligible (governed result, not unconditional 403).
- Allow `POST /v1/twin/snapshots/{id}/authorize` to succeed when Permission allows
  and snapshot is eligible (governed result, not unconditional 403).
- Audit intent/result for allow and deny; regression tests for both paths.
- Status honesty: status surfaces report execution as `permission_gated`.

## Out of Scope

- Unrestricted Brain-driven auto SO/DO/invoice/receipt/AP/RET/GL writes
- Cap→grant, Twin `authorize_execution=true` as global default without Permission
- Opening host network installs; silent removal of Z3 advisory
- Any milestone other than PHX-G335

## Open Decisions

- Milestone ID: **PHX-G335** — confirmed
- Alembic: **none**
- Whether execute may enqueue Workflow approval for high-impact actions (Defer)

## Risks

**High** — first lift of constitutional fail-closed execution fences. Mis-wiring can
create unauthorized commercial side effects. Mitigate with Permission default-deny,
audit, and contract tests that still deny unprivileged callers.

## Recommendation

Approve Design Boundary, then Approve Coding Authorization with **explicit**
milestone PHX-G335. Do not treat Z3 COMPLETE as authorization to open execute.

## Product Owner response

```text
Design Gate: Approve
Coding Auth: Approve Milestone PHX-G335
Alembic: none
Signer: Product Owner — Shawn — 2026-07-26
```

**Disposition:** Approved. Design boundary authorized. Coding Auth recorded on
[Coding Authorization Summary](BRAIN_TWIN_EXECUTION_CODING_AUTHORIZATION_SUMMARY.md).
