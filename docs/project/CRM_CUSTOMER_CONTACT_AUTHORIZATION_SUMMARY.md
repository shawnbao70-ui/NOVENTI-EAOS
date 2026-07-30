# Decision Summary — CRM Customer + Contact

> Phoenix Gate Framework pilot ([ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md) · [PHOENIX_GATE_FRAMEWORK](PHOENIX_GATE_FRAMEWORK.md)).  
> Product Owner decision surface only. Generated Gate artifacts are not the PO form.

## Package

`noventi.crm` — CRM Customer + Contact

## Purpose

Define the tenant-scoped business boundary for Customer and Contact management.

## Scope

Design boundary only. Business Package ownership; Kernel unchanged. No CRUD, API, SQL, service, UI, Alembic, runtime manifest, milestone, or coding authorization.

## Architecture Boundary

- Customer/Contact belong to Business Package `noventi.crm`, not Kernel.
- Consume Tenant, Permission Evaluate, Audit, and Event Outbox contracts; do not fork platform truth sources.
- Customer is not Tenant / Enterprise / Org Unit / Membership; Contact is not Identity Subject or Permission Principal.
- Permission remains default-deny; owner/territory never grant access.

## In Scope

- Customer aggregate root semantics, identity, and lifecycle boundary
- Contact as Customer-owned child entity, PII/minimization boundary, optional primary-contact relation
- Package ownership and resource type candidates `pkg.crm.customer` / `pkg.crm.contact`
- Explicit separation: Accepted knowledge ≠ Gate Accept ≠ Coding Authorization

## Out of Scope

- Opportunity, Quote/Convert, Sales Order, Finance/AR, Follow-up, Customer360, search/import/merge
- Contact roles/decision-power/backup escalation, Brain/Twin, Legacy architecture inheritance
- CRUD, SQL/API/services, Alembic, UI, runtime manifest register/publish/install
- Any implementation milestone or coding authorization

## Open Decisions

- Single Customer lifecycle; archive preferred over hard delete → Accept proposed
- Contact child-entity + optional primary-contact boundary → Accept proposed
- Channel deduplication, territory, runtime events, high-impact workflow → Defer out of gate
- Resource-scoped fail-closed authorization boundary → Accept proposed; detailed action/masking matrices remain separate design contracts

## Risks

Medium — Contact privacy and lifecycle semantics require later control-owner detail review; no runtime risk is opened by this design-only approval.

## Recommendation

Accept Design Boundary. Architecture approval only; coding authorization remains `None`.

## Product Owner response

**Approve — 2026-07-24 (explicit conversation authorization).**

## Status

Approved — design boundary only; coding authorization on this design surface = None.  
Phase G（2026-07-26）：Product Owner **Shawn** — Design Gate **Reaffirm**；C1 Coding Auth PHX-G294 **Affirm**（独立表面）。  
Generated artifacts: [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md) · [Architecture Gate](CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md) · [Acceptance](CRM_CUSTOMER_CONTACT_ACCEPTANCE.md) · [Proposed manifest](../../packages/crm/manifest.proposed.json).  
Historical review evidence: [CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md](CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md) — **RETIRED; original TRACK-G COMPLETE record preserved**.
