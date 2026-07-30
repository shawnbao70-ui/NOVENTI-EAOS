# Decision Summary — CRM Customer + Contact Minimal List Query Boundary

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-28. Generated artifacts are not Product
> Owner editing surfaces.

## Package

CRM — Customer + Contact Minimal List Query Boundary

## Purpose

Provide governed Customer and Contact collection reads required to unblock the
PHX-G512 read-only CRM UI.

## Scope

Design tenant-scoped `GET /v1/crm/customers` and
`GET /v1/crm/customers/{customer_id}/contacts` query contracts.

## Architecture Boundary

The queries remain CRM Package-owned. Tenant authority comes only from trusted
ExecutionContext, Customer/Contact `read` Permission remains default-deny, and
the client cannot override tenant context. Contact collection data is
minimized. No Kernel change is accepted.

## In Scope

- Tenant-scoped service and Repository list queries
- Closed paginated response DTOs
- `limit` bounds and opaque cursor
- Active-only default result set
- Minimal Customer collection fields
- Contact collection fields limited to ID, name, title, and status
- Tenant, Permission, PII, OpenAPI, and contract evidence

## Out of Scope

- Business writes
- Database schema or Alembic changes
- Search, fuzzy matching, import, or merge
- Customer 360
- Contact email or phone in collection responses
- Runtime Manifest changes
- A new milestone or production promotion

## Open Decisions

1. Default `limit=50`; maximum `limit=100`.
2. Opaque cursor with stable `updated_at + id` ordering.
3. Archived records are excluded by default.
4. Contact email and phone remain available only through the existing
   permission-governed Contact detail endpoint.
5. Any implementation authorization must extend the same PHX-G512 milestone;
   this Gate does not authorize code.

## Risks

- Pagination must not expose cross-tenant records.
- Contact collections can expand PII exposure if field minimization drifts.
- Repository implementations can produce unstable pagination.
- Gate acceptance could be mistaken for automatic G512 resume.

## Recommendation

Approve the minimal read-only collection-query design boundary. Keep
`Coding Authorization: None` until a separate PHX-G512 prerequisite
implementation authorization is explicitly approved.
