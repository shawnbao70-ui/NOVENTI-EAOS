# Decision Summary — CRM Opportunity (C2)

> Phoenix Gate Framework ([ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)).  
> Product Owner reads **only this page**, then replies: `Approve` · `Amend: <comment>` · `Reject`  
> Approve = design boundary only. Coding authorization remains `None`.  
> Prerequisite: PHX-G294 Customer+Contact C1 COMPLETE.

## Package

`noventi.crm` — Opportunity (sales pipeline opportunity aggregate)

## Purpose

Define the tenant-scoped product boundary for CRM Opportunity as the next slice after Customer + Contact, without opening Requirement / Quote / Convert / AI insight engines.

## Scope

Design boundary only. Extends Business Package `noventi.crm`. Kernel unchanged. No CRUD, API, SQL, Alembic, UI, runtime manifest install, milestone, or coding authorization from this Approve.

## Architecture Boundary

- Opportunity belongs to `noventi.crm`, not Kernel; consumes Tenant, Permission Evaluate, Audit, Event Outbox contracts.
- Opportunity references an existing same-tenant Customer (from C1); it is not a Customer substitute and not an Organization entity.
- Owner/salesperson is a business responsibility reference only; never substitutes Permission.
- Legacy “customer opportunity mining” stubs and “Enterprise Opportunity Engine” AI insight cards are **different capability types** and stay Out.
- Accepted knowledge (ADR-0309 / opportunity.md) ≠ this Gate Accept ≠ coding authorization.

## In Scope

- Opportunity as CRM aggregate: opaque tenant-scoped ID, title, link to Customer, lifecycle status boundary, source/priority as product vocabulary candidates, owner reference, archive-oriented deletion posture
- Package resource type candidate `pkg.crm.opportunity`
- Permission default-deny; write intents/results auditable in a future coding slice
- Explicit chain position: after Customer, before Requirement (graph position only — Requirement not implemented here)

## Out of Scope

- Requirement, Analysis, Sample, Quote/Quotation, Convert, Sales Order
- Finance / AR, Follow-up, Customer360, import/merge/dedup, keyword search projections
- AI Opportunity Engine / mining stubs / insight→CRM auto-insert
- Brain execute / Twin authorize / Cap→grant
- Legacy table/route/role/SQL inheritance; runtime event schema publish
- Any C2 coding, Alembic, or second milestone from this Summary alone

## Open Decisions

- Customer required on create for sales Opportunity → Accept proposed  
- Single product lifecycle vocabulary (not Legacy doc-only `open→qualified→converted→closed` as proven fact) → Accept proposed; exact tokens may Amend in design docs  
- System-assigned opportunity code preferred → Accept proposed  
- Requirement child flow / requirement_count → Defer out of gate (C3+ candidate)  
- Quote linkage / convert → Defer out of gate  
- Source/priority full enums → Accept minimal set; detailed taxonomy Defer/Amend in design  
- AI insight conversion into Opportunity rows → Defer out of gate (explicit future product decision)

## Risks

Medium — Legacy permission and state-machine evidence is inconsistent; design must not ship undocumented Legacy behavior as accepted fact. No runtime risk from design-only Approve.

## Recommendation

Accept Design Boundary for Opportunity (C2). Architecture approval only; coding authorization remains `None` until a separate Coding Authorization Summary + milestone (expected next free PHX-G after G294, only when you authorize coding).

## Product Owner response

_Pending — paste exactly one of:_

```text
Approve
```

```text
Amend: <concise comment>
```

```text
Reject
```
