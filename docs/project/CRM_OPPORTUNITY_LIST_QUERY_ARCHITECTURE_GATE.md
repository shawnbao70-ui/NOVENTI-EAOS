# Architecture Gate — CRM Opportunity Minimal List Query

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Approved Decision Summary:
  [CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md](CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_OPPORTUNITY_LIST_QUERY_APPROVAL_RECORD.md](CRM_OPPORTUNITY_LIST_QUERY_APPROVAL_RECORD.md)
- Evidence:
  [G514 HOLD](CRM_OPPORTUNITY_UI_G514_HOLD.md) ·
  `api/gateway/routers/crm.py` · `api/gateway/schemas/crm.py` ·
  `noventi/crm/repository.py`

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- G514 implementation: **HOLD**

## Generated boundary

### Purpose

Add a minimal governed Opportunity collection query so G514 can eventually
render a truthful list.

### Scope

Tenant-scoped active Opportunity collection read with a closed minimal DTO and
bounded opaque-cursor pagination.

### Architecture Boundary

CRM owns the API, Service, and Repository contracts. Trusted ExecutionContext
supplies tenant authority. Opportunity `read` Permission is default-deny.
Kernel and Database schema remain unchanged.

### In Scope

- `GET /v1/crm/opportunities`
- Closed list envelope and approved list-item fields
- Default `limit=50`, maximum `100`
- Opaque cursor using stable `updated_at + id`
- Active-only default
- Tenant, Permission, OpenAPI, and pagination contracts

### Out of Scope

- Writes, search, scoring, forecasting, import, merge, and automation
- Requirement, Quote, Sales Order, Customer 360, or adjacent packages
- Database, Alembic, Kernel, Runtime Manifest, and frontend changes
- Milestone opening, successor slices, or production promotion

## OD dispositions

| OD | Decision | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Pagination bounds | Accepted — default 50, maximum 100 | approved Summary |
| OD-02 | Cursor/order | Accepted — opaque, `updated_at + id` | approved Summary |
| OD-03 | Archived visibility | Accepted — excluded | approved Summary |
| OD-04 | List projection | Accepted — fixed minimal fields | approved Summary |
| OD-05 | G514 state | Accepted — HOLD pending coding approval | Approval Record |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | CRM / Kernel boundary | Pass | Summary |
| RC-02 | Tenant isolation | Pass — trusted context only | Summary |
| RC-03 | Permission default-deny | Pass — Opportunity read required | Summary |
| RC-04 | Minimal collection exposure | Pass | approved fields |
| RC-05 | Stable bounded pagination | Pass at design level | Summary |
| RC-06 | No schema migration | Pass | Out of Scope |
| RC-07 | State separation | Pass — coding remains None | Approval Record |
| RC-08 | Serial stop | Pass — G514 HOLD, successors closed | HOLD |

Missing implementation evidence is not inferred as Pass.

## Risks

Tenant-filter drift, unstable cursor ordering, owner-identifier exposure, and
authorization-state confusion remain controlled by the accepted boundary.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approval meaning: list-query design boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- Existing detail/write Opportunity routes: available
- G514 interface-gap HOLD: available
- Collection-query implementation evidence: missing by design

## Implementation boundary

No API, Service, Repository, frontend, Database, Alembic, Runtime Manifest,
milestone resume, or production work is authorized by this Gate.
