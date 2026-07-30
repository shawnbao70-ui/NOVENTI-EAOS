# Architecture Gate — CRM Customer + Contact Minimal List Query

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Package ADR: [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)
- Approved Decision Summary:
  [CRM_CUSTOMER_CONTACT_LIST_QUERY_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_LIST_QUERY_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_CUSTOMER_CONTACT_LIST_QUERY_APPROVAL_RECORD.md](CRM_CUSTOMER_CONTACT_LIST_QUERY_APPROVAL_RECORD.md)
- Evidence:
  [PHX-G512 HOLD](CRM_CUSTOMER_CONTACT_UI_G512_HOLD.md) ·
  `api/gateway/routers/crm.py` · `api/gateway/schemas/crm.py`

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- Implementation Milestone: **None on this Gate**

## Generated boundary

### Purpose

Add a minimal governed collection-query boundary so PHX-G512 can eventually
render truthful Customer and Contact lists.

### Scope

The accepted design consists of tenant-scoped Customer and nested Contact
collection reads with bounded opaque-cursor pagination.

### Architecture Boundary

CRM owns the API, service, and Repository contracts. Trusted
ExecutionContext supplies tenant authority. Permission remains resource
specific and default-deny. Collection DTOs minimize Contact PII. Kernel and
Database schema remain unchanged.

### In Scope

- `GET /v1/crm/customers`
- `GET /v1/crm/customers/{customer_id}/contacts`
- Closed list envelopes and minimal list-item DTOs
- Default `limit=50`, maximum `100`
- Opaque cursor with stable `updated_at + id` order
- Active-only default
- Tenant, Permission, PII, OpenAPI, and contract validation

### Out of Scope

- Writes, search, import, merge, and Customer 360
- Contact email/phone in collection responses
- Database, Alembic, Kernel, and Runtime Manifest changes
- Frontend implementation under this Gate
- Production promotion or a second milestone

## OD dispositions

| OD | Decision from approved Summary | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Pagination bounds | Accepted — default 50, maximum 100 | approved Summary |
| OD-02 | Cursor and ordering | Accepted — opaque, `updated_at + id` | approved Summary |
| OD-03 | Archived visibility | Accepted — excluded by default | approved Summary |
| OD-04 | Contact PII | Accepted — email/phone excluded from list | approved Summary |
| OD-05 | Milestone handling | Accepted — same PHX-G512 only after separate authorization | approved Summary |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | Package / Kernel boundary | Pass | ADR-0320 / Summary |
| RC-02 | Tenant isolation | Pass — trusted context only | Summary |
| RC-03 | Permission default-deny | Pass — Customer/Contact read required | ADR-0320 |
| RC-04 | Contact PII minimization | Pass — collection fields constrained | Summary |
| RC-05 | No schema migration | Pass | Out of Scope |
| RC-06 | State separation | Pass — coding remains None | Approval Record |

Missing implementation evidence is not inferred as Pass.

## Risks

- Cursor implementation could leak or skip tenant records.
- PII minimization could drift from the accepted list DTO.
- Ordering could differ across Repository implementations.
- This Gate could be mistaken for implementation authorization.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approved Summary:
  [CRM_CUSTOMER_CONTACT_LIST_QUERY_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_LIST_QUERY_DECISION_SUMMARY.md)
- Approval meaning: design boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- Existing detail-only CRM Gateway and closed DTOs: available
- PHX-G512 interface-gap HOLD: available
- Collection-query implementation evidence: missing by design

## Implementation boundary

No API, service, Repository, frontend, Database, Alembic, Runtime Manifest,
milestone resume, or production work is authorized by this Gate.
