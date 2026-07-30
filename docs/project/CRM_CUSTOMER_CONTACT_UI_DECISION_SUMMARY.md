# Decision Summary — CRM Customer + Contact UI

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated Gate artifacts are not
> Product Owner editing surfaces.

## Package

CRM — Customer + Contact UI

## Purpose

Establish the first CRM Customer and Contact business UI boundary for
navigation, tenant-safe presentation, permission-aware states, and basic user
flow validation.

## Scope

The first slice is a read-only UI shell. It may consume existing governed query
interfaces when compatible, but this Gate creates no backend capability.

## Architecture Boundary

The UI belongs to the CRM Business Package and does not enter Kernel. It does
not accept user-supplied tenant context as authority and does not perform local
authorization in place of server-side Permission evaluation.

## In Scope

- CRM navigation and page layout
- Customer list and detail presentation
- Contact list and detail presentation
- Loading, empty, denied, and error states
- Default-hidden or non-actionable presentation for unauthorized operations
- Read-only audit correlation presentation when already available

## Out of Scope

- New or modified CRUD, API, Repository, Database, or Alembic behavior
- Customer or Contact business writes
- Import, merge, Customer 360, Finance, Workflow, Brain, or Twin capabilities
- Runtime Manifest changes
- Client-side authorization as a security boundary
- Automatic business writes

## Open Decisions

1. Use a read-only UI shell for the first slice.
2. Existing CRM query interfaces may be reused only when already governed and
   compatible; interface gaps require a separate Gate and authorization.
3. Write actions remain out of scope. Disabled placeholders versus complete
   omission is deferred; neither may become actionable in this slice.

## Risks

- Existing query interfaces may not provide all desired presentation data.
- Hidden or disabled controls cannot replace server-side authorization.
- A visible UI can be mistaken for business-write authorization.

## Recommendation

Approve the read-only CRM Customer + Contact UI design boundary. Keep
`Coding Authorization: None` until a separate UI Coding Authorization is
explicitly approved.
