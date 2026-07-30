# Decision Summary — CRM Sales Order Minimal List Query

> **Only Product Owner approval entry**  
> Approved in conversation on 2026-07-29.

## Package

CRM — Sales Order Minimal List Query

## Purpose

Provide the Sales Order collection read required to unblock G519.

## Scope

Design tenant-scoped `GET /v1/crm/sales-orders` with bounded opaque-cursor
pagination and a closed minimal DTO.

## Architecture Boundary

CRM-owned API/Service/Repository. Trusted ExecutionContext supplies Tenant
authority; Sales Order `read` Permission is default-deny. No schema or Kernel
change. Cursor uses existing `created_at + id` because Sales Order has no
`updated_at` column.

## In Scope

- Tenant Sales Order collection across existing lifecycle statuses
- Default limit 50; maximum 100
- Opaque `created_at + id` cursor
- Fields: ID, conversion ID, quote ID, requirement ID, code, currency, status,
  total amount, created time, version
- Closed DTO/envelope and tenant/Permission/OpenAPI/pagination contracts

## Out of Scope

- Confirm, Delivery, Invoice, Return Authorization, writes
- FX fields beyond existing detail DTOs, search, fulfillment automation
- Database, Alembic, Kernel, Runtime Manifest, frontend, production
- G519 resume or G520+

## Open Decisions

1. All existing Sales Order statuses are visible; there is no archive status.
2. Default limit 50; maximum 100.
3. Cursor order is `created_at + id`.
4. Projection is fixed to approved fields.
5. G519 stays HOLD pending separate Coding Authorization.

## Risks

Tenant-filter drift, unstable cursors, status/total projection drift, and
accidental Confirm write exposure.

## Recommendation

Approve the design and retain `Coding Authorization: None`.
