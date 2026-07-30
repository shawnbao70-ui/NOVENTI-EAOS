# Coding Authorization Summary — Brain Execute + Twin Authorize Open

> Phoenix Gate Framework (ADR-0321). **Independent** from Z3 advisory.  
> **Status: Approved — PHX-G335 coding authorized (Alembic none).**

## Package

`eaos_platform.brain` / `eaos_platform.twin` — Execution open slice

## Purpose

Authorize replacing unconditional fail-closed execute/authorize with
Permission-gated success/deny paths for milestone PHX-G335 only.

## Scope

Coding authorization granted after PO Approve on this page + milestone ID.
Does not authorize Cap→grant, silent commercial auto-writes, or network installs.

## Architecture Boundary

- Must follow [Decision Summary](BRAIN_TWIN_EXECUTION_AUTHORIZATION_SUMMARY.md)
- Must follow [ADR-0367](../decisions/ADR-0367-brain-twin-execution-open-boundary.md) (Accepted)
- Z3 advisory remains read-only; `execution_authority: "none"` on advisory envelopes
- Tenant / Permission / Audit invariants unchanged

## In Scope

- Lift unconditional `BRAIN_EXECUTION_FORBIDDEN` / `TWIN_EXECUTION_FORBIDDEN` only
  when Permission allow + eligibility checks pass
- Keep 403 + stable codes for deny / unprivileged / ineligible
- Gateway status honesty (`permission_gated`)
- Contract + gateway tests: allow path + deny path + Z3 advisory regress
- Milestone **PHX-G335**; Alembic **none**

## Out of Scope

- Cap→grant; Brain/Twin driving CRM/Finance/Purchase writes without separate slice
- Removing audit; opening PSP/tax network (already separate)
- AP/RET/GL new features

## Open Decisions

- Milestone ID: **PHX-G335** (confirmed)
- Alembic: **none** (confirmed)
- High-impact Workflow step: Defer

## Risks

High — execution fence lift. Require deny-path tests green before merge.

## Prerequisites

- Decision Summary Approve — recorded
- Tip: `0064_purchase_three_way_match_g334`
- Z3 advisory COMPLETE

## Product Owner response

```text
Design Gate: Approve
Coding Auth: Approve Milestone PHX-G335
Alembic: none
Signer: Product Owner — Shawn — 2026-07-26
```

**Disposition:** Coding authorized for PHX-G335 only. Tip remains
`0064_purchase_three_way_match_g334`. No Alembic.
