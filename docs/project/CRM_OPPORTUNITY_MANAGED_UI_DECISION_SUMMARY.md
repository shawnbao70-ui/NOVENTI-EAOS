# Decision Summary — CRM Opportunity Managed UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated artifacts are not Product
> Owner editing surfaces.

## Package

CRM — Opportunity Managed UI

## Purpose

Provide governed Opportunity list, detail, create, edit, and archive workflows
in Smart Terminal.

## Scope

Frontend design over the existing CRM Opportunity API boundary. This is the
first independently gated slice in the approved CRM Business UI serial plan.

## Architecture Boundary

CRM owns the UI. Tenant and actor authority come only from trusted context;
server Permission remains authoritative. Updates and archives use
`expected_version`, audit correlation is preserved, and archive replaces hard
delete.

## In Scope

- Opportunity list and detail
- Create and edit forms
- Archive reason and explicit confirmation
- Customer association using governed Customer records
- Permission-projected write controls
- Loading, empty, denied, missing, conflict, and validation states
- Frontend contracts and browser verification after Coding Authorization

## Out of Scope

- New or modified API, Service, Repository, Database, or Alembic behavior
- Opportunity stage automation, scoring, forecasting, import, merge, or bulk
  operations
- Requirement, Quote, Sales Order, Finance, Brain, or Twin expansion
- Runtime Manifest, automatic writes, hard delete, production promotion
- Opening any successor serial slice

## Open Decisions

1. Existing APIs are the only permitted implementation dependency.
2. Missing list/write capability places G514 on HOLD and stops the serial plan.
3. Write controls are absent when effective Permission is unavailable.
4. A 409 conflict stops submission and refreshes current governed data.
5. Coding remains independently authorized; no milestone is opened by this
   Gate.

## Risks

- The existing Opportunity API may lack a bounded collection query.
- Customer association can cross tenant boundaries if trusted context is
  bypassed.
- Hidden controls cannot replace server-side authorization.
- Stale versions can create concurrency conflicts.
- UI completion can be mistaken for production authorization.

## Recommendation

Approve the Opportunity Managed UI design boundary. Keep
`Coding Authorization: None` until PHX-G514 is independently approved.
