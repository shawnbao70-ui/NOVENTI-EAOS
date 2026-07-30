# Coding Authorization Summary — CRM Customer + Contact (C1)

> Phoenix Gate Framework ([ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)).  
> **Independent** from design-only Gate Accept. Product Owner decision surface only.

## Package

`noventi.crm` — Customer + Contact minimal vertical slice (C1)

## Purpose

Authorize implementation of the first CRM write/read slice strictly inside the accepted Customer + Contact design boundary.

## Scope

Coding authorization for C1 only. Does not accept Opportunity/Quote/Finance/Brain. Does not invent deferred OD detail as product law beyond Gate Accept.

## Architecture Boundary

- Must follow [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md) and Gate Accepted artifacts
- Package `noventi.crm` ≠ Kernel; Tenant/Permission fail-closed; owner/territory never authorize
- No Brain execute / Twin authorize / Cap→grant
- No Legacy SQL/table/route/role inheritance

## In Scope

- Customer + Contact persistence, API/service, permissioned read/write/archive paths as required for the minimal slice
- Tenant isolation, audit of write intents/results, tests proving fail-closed cross-tenant deny
- Package-owned opaque IDs; proposed manifest remains non-runtime until separately authorized to register

## Out of Scope

- Opportunity, Quote/Convert, SO, Finance, Follow-up, Customer360, import/merge/dedup
- Contact role/decision-power/backup strategies; runtime event schema publish
- U236+ unrelated Foundation deepen; inventing undeclared product milestones

## Open Decisions

- Milestone ID: **PHX-G294**（Product Owner authorized the next available
  contiguous milestone after PHX-G293；不得另开第二里程碑）
- Detailed field/action/masking matrices may be designed inside C1 only insofar as required by accepted boundary; deferred ODs stay deferred

## Risks

Medium — first business write path; must not collapse Permission into owner filters or skip audit.

## Recommendation

Approve Coding Authorization for C1 **only after** Product Owner assigns an explicit milestone ID in the response.

## Prerequisites

- Design Gate: [Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md) Approved; Gate Accepted (design boundary only)
- Baseline: TRACK-A COMPLETE (integration 19 + contracts 1622)
- Milestone: **PHX-G294**

## Product Owner response

```text
Approve
Milestone: next available PHX-G after G293
Authorization agent may select and persist the next free number; do not skip
numbers or open a second milestone.
```

Recorded milestone: **PHX-G294**（2026-07-24）

## Phase G reaffirmation

```text
Coding Auth (PHX-G294): Affirm
Signer: Product Owner — Shawn — 2026-07-26
Historical evidence (retired workflow): CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md
```

Status: **Affirmed** — C1 coding authorization for PHX-G294 remains in force.  
Does not authorize Opportunity/Quote/Finance slices, runtime manifest register/publish/install, Brain/Twin, or a second parallel milestone.
