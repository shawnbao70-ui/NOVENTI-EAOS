# Architecture Gate — CRM Quote Header Minimal List Query

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Approved Summary](CRM_QUOTE_HEADER_LIST_QUERY_DECISION_SUMMARY.md)
- [Approval Record](CRM_QUOTE_HEADER_LIST_QUERY_APPROVAL_RECORD.md)
- [G516 HOLD](CRM_QUOTE_HEADER_UI_G516_HOLD.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- G516: **HOLD**

## Generated boundary

### Purpose

Add the minimal Quote Header collection query required by G516.

### Scope

Tenant-scoped, non-archived, cursor-paginated Quote Headers with a closed
minimal projection.

### Architecture Boundary

CRM-owned API/Service/Repository; trusted Tenant context; Quote read Permission
default-deny; no schema or Kernel change.

### In Scope

- `GET /v1/crm/quotes`
- Draft and issued statuses
- Default 50 / maximum 100
- Opaque `updated_at + id` cursor
- Approved fields and closed envelope

### Out of Scope

- Notes, lines, issue, convert, totals, approvals, writes
- Persistence schema, runtime, frontend, production, successors

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Visibility | Draft/issued; archived excluded |
| OD-02 | Pagination | 50 default / 100 maximum |
| OD-03 | Cursor | Opaque `updated_at + id` |
| OD-04 | Projection | Fixed approved fields |
| OD-05 | G516 | HOLD pending coding approval |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Minimal projection | Pass |
| RC-05 | Status/currency honesty | Pass at design level |
| RC-06 | No migration | Pass |
| RC-07 | State separation | Pass |
| RC-08 | Serial stop | Pass |

## Risks

Tenant-filter drift, cursor instability, projection drift, and accidental line
or notes exposure remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

Existing Quote routes and G516 HOLD are available. Implementation evidence is
not inferred.

## Implementation boundary

No implementation or milestone resume is authorized.
