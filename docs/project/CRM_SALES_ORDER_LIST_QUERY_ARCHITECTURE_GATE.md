# Architecture Gate — CRM Sales Order Minimal List Query

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_SALES_ORDER_LIST_QUERY_DECISION_SUMMARY.md)
- [Approval Record](CRM_SALES_ORDER_LIST_QUERY_APPROVAL_RECORD.md)
- [G519 HOLD](CRM_SALES_ORDER_UI_G519_HOLD.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define the minimal Sales Order collection read that unblocks G519.

### Scope

`GET /v1/crm/sales-orders` with bounded cursor pagination and closed minimal
DTO. Confirm and fulfillment remain outside.

### Architecture Boundary

CRM-owned API/Service/Repository; trusted Tenant context; Permission
default-deny; no Database/Alembic/Kernel/Runtime Manifest change; cursor on
`created_at + id`.

### In Scope

- Collection read for existing Sales Order statuses
- Limit 1–100; default 50
- Opaque cursor and closed list DTO/envelope
- Tenant and Permission contracts

### Out of Scope

- Confirm, Delivery, Invoice, Return Auth, writes
- Frontend implementation, production, G520+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Status visibility | All existing statuses |
| OD-02 | Limit | Default 50 / max 100 |
| OD-03 | Cursor | `created_at + id` |
| OD-04 | Projection | Fixed approved fields |
| OD-05 | G519 HOLD | Remains until Coding Authorization |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | No schema change | Pass |
| RC-05 | No Confirm write expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Tenant-filter drift, cursor instability, total/status projection drift, and
Confirm-scope leakage remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

G519 HOLD and existing Sales Order contracts are available; implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
