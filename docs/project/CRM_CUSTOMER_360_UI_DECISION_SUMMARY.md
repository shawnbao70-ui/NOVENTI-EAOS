# Decision Summary — CRM Customer 360 Read-only Composition

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29 (AK→AR second slice).

## Package

CRM — Customer 360 Read-only Composition

## Purpose

Provide a governed read-only Customer 360 composition for the selected
Customer so commercial-chain context is visible in one surface.

## Scope

Second CRM Business UI serial AK→AR slice; candidate PHX-G521. Read-only
composition only; no Commercial Hold write, Quote Issue, Delivery, Invoice,
or Return Authorization UI.

## Architecture Boundary

CRM-owned Smart Terminal UI over the existing
`GET /v1/crm/customers/{id}/360` projection. Trusted context supplies Tenant
and actor; server Permission remains authoritative. Projection fields
(including counts and invoice/receipt/credit traces) are server-owned.
No Finance GL write path is invented.

## In Scope

- Customer 360 read-only panel for the selected Customer
- Display of commercial_hold and open-order counts
- Read-only invoice / receipt / credit-note traces
- Permission-projected controls and fail-closed states
- Frontend contracts and browser evidence after Coding Authorization

## Out of Scope

- Commercial Hold write (G527)
- Quote Issue, Delivery, Invoice, Return Authorization
- Database, Alembic, Kernel, Runtime Manifest
- Finance GL, Brain, Twin, production, automatic writes
- G522+

## Open Decisions

1. Existing `/360` endpoint is the sole API dependency.
2. No Customer selection means no 360 load.
3. Traces are read-only; clicks do not open Invoice/Receipt write UI.
4. Missing prerequisite places G521 on HOLD.

## Risks

PII or financial-trace scope creep, accidental Hold/Issue opening, and
cross-domain Finance drift.

## Recommendation

Approve this design boundary and retain `Coding Authorization: None`.
