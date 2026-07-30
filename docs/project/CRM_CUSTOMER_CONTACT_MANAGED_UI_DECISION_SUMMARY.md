# Decision Summary — CRM C18 Customer + Contact Managed UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated artifacts are not Product
> Owner editing surfaces.

## Package

CRM — C18 Customer + Contact Managed UI

## Purpose

Extend the accepted read-only CRM surface with governed create, edit, and
archive user flows for Customer and Contact.

## Scope

Design frontend write workflows that reuse existing CRM APIs. No backend,
Database, migration, or Runtime capability is created by this Gate.

## Architecture Boundary

The UI remains CRM Package-owned. Tenant authority comes only from trusted
context; server-side Permission remains authoritative. Writes use
`expected_version`, preserve audit correlation, and use archive instead of
hard delete.

## In Scope

- Customer create, edit, and archive flows
- Contact create, edit, and archive flows
- Form validation and Contact PII minimization
- 403, 404, 409, and 422 presentation
- Required archive reason and explicit confirmation
- List/detail refresh after successful writes
- Frontend contracts and browser verification

## Out of Scope

- Hard delete
- Customer merge, import, deduplication, or commercial hold
- Customer 360
- New or modified API, Repository, Database, or Alembic behavior
- Runtime Manifest changes
- Finance, Workflow, Brain, or Twin expansion
- Automatic/bulk business writes and production promotion

## Open Decisions

1. Archive requires explicit secondary confirmation and a reason.
2. A 409 conflict stops submission and refreshes the latest version.
3. Contact email and phone remain optional and are never inferred.
4. Write controls are absent when Permission does not allow the operation.
5. Coding remains separately authorized; this Gate creates no milestone.

## Risks

- Stale frontend state can create optimistic-concurrency conflicts.
- Contact forms can expand sensitive-data exposure.
- Hidden controls cannot replace server-side authorization.
- Archive can be mistaken for deletion.
- UI completion can be mistaken for production GO.

## Recommendation

Approve the CRM C18 Managed UI design boundary. Keep
`Coding Authorization: None` until PHX-G513 is independently approved.
