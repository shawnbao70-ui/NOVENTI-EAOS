# Decision Summary — CRM Requirement Managed UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Requirement Managed UI

## Purpose

Provide governed Requirement list, detail, create, edit, and archive workflows
as the second CRM Business UI serial slice.

## Scope

Frontend design for CRM Requirement records and their governed Opportunity
association. Candidate milestone: PHX-G515.

## Architecture Boundary

CRM owns the UI. Tenant and actor authority come only from trusted context;
server Permission remains authoritative. Updates and archives use
`expected_version`; archive replaces hard delete.

## In Scope

- Requirement list and detail
- Create, edit, and archive forms
- Governed Opportunity association
- Permission-projected write controls
- Loading, empty, denied, missing, conflict, and validation states
- Frontend contracts and browser verification after Coding Authorization

## Out of Scope

- New backend capability unless separately gated and authorized
- Database, Alembic, Kernel, or Runtime Manifest changes
- Quote, conversion, Sales Order, Finance, Brain, or Twin expansion
- Search, import, merge, bulk/automatic writes, hard delete, production
- G516 or later slices

## Open Decisions

1. Existing APIs are the only initial implementation dependency.
2. Missing collection capability places G515 on HOLD.
3. Opportunity association must come from governed records.
4. 409 stops submission and refreshes current data without overwrite.
5. Coding remains independent; G515 is not opened by this Gate.

## Risks

Requirement collection APIs may be absent; association can cross tenant
boundaries if trusted context is bypassed; stale versions can conflict; hidden
controls cannot replace server authorization.

## Recommendation

Approve the design boundary and retain `Coding Authorization: None`.
