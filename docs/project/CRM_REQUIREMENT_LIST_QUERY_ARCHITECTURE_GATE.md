# Architecture Gate — CRM Requirement Minimal List Query

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0323](../decisions/ADR-0323-crm-requirement-product-boundary.md)
- [Approved Summary](CRM_REQUIREMENT_LIST_QUERY_DECISION_SUMMARY.md)
- [Approval Record](CRM_REQUIREMENT_LIST_QUERY_APPROVAL_RECORD.md)
- [G515 HOLD](CRM_REQUIREMENT_UI_G515_HOLD.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- G515: **HOLD**

## Generated boundary

### Purpose

Add the minimal Requirement collection query required by G515.

### Scope

Tenant-scoped, active-only, cursor-paginated Requirement collection with a
closed minimal projection.

### Architecture Boundary

CRM-owned API/Service/Repository; trusted Tenant context; Requirement read
Permission default-deny; no Kernel or schema change.

### In Scope

- `GET /v1/crm/requirements`
- Default limit 50, maximum 100
- Opaque `updated_at + id` cursor
- Approved minimal fields and closed envelope
- Tenant, Permission, OpenAPI, pagination contracts

### Out of Scope

- Writes, search, automation, downstream slices
- Database, Alembic, Kernel, Runtime Manifest, frontend, production

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Pagination | 50 default / 100 maximum |
| OD-02 | Visibility | Active-only |
| OD-03 | Cursor | Opaque `updated_at + id` |
| OD-04 | Projection | Fixed minimal fields |
| OD-05 | G515 | HOLD pending coding approval |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Minimal projection | Pass |
| RC-05 | Bounded pagination | Pass at design level |
| RC-06 | No migration | Pass |
| RC-07 | State separation | Pass |
| RC-08 | Serial stop | Pass |

Implementation evidence is not inferred.

## Risks

Tenant-filter drift, unstable cursors, projection expansion, and authorization
confusion remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

Existing Requirement detail/write routes and G515 HOLD are available.

## Implementation boundary

No implementation or milestone resume is authorized.
