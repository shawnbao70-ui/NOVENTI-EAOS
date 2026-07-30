# Architecture Gate — CRM C18 Customer + Contact Managed UI

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Package ADR: [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)
- Approved Decision Summary:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_APPROVAL_RECORD.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_APPROVAL_RECORD.md)
- Evidence:
  [PHX-G512 Acceptance](CRM_CUSTOMER_CONTACT_UI_G512_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Customer and Contact create, edit, and archive UX over the
existing CRM API boundary.

### Scope

Frontend-only managed-record workflows with validation, concurrency conflict
handling, Permission-aware controls, explicit archive confirmation, and
post-write refresh.

### Architecture Boundary

CRM owns the UI. Trusted context supplies Tenant and actor identity.
Server-side Permission remains authoritative. Updates and archives carry
`expected_version`; hard delete and inferred PII are prohibited.

### In Scope

- Customer and Contact create/edit/archive forms
- Required archive reason and confirmation
- 403/404/409/422 handling
- Optional, non-inferred Contact email/phone
- List/detail refresh after success
- Frontend tests and browser evidence

### Out of Scope

- Backend/API/Repository/Database/Alembic changes
- Hard delete, merge, import, deduplication, commercial hold, Customer 360
- Runtime Manifest, adjacent domains, bulk/automatic writes, production

## OD dispositions

| OD | Decision | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Archive confirmation and reason | Accepted | approved Summary |
| OD-02 | 409 conflict behavior | Accepted — stop and refresh | approved Summary |
| OD-03 | Contact PII | Accepted — optional, never inferred | approved Summary |
| OD-04 | Unauthorized write controls | Accepted — absent | approved Summary |
| OD-05 | Coding separation | Accepted — remains None | Approval Record |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | Package / Kernel boundary | Pass | ADR-0320 |
| RC-02 | Tenant trusted context | Pass | Summary |
| RC-03 | Permission default-deny | Pass | Summary |
| RC-04 | Optimistic concurrency | Pass | Summary |
| RC-05 | PII minimization | Pass | Summary |
| RC-06 | No backend/runtime expansion | Pass | Out of Scope |
| RC-07 | Coding state separation | Pass | Approval Record |

## Risks

Stale state, PII exposure, authorization confusion, archive semantics, and
production-status confusion remain constrained by the accepted boundary.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approval meaning: design boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- Existing CRM write API contracts: available
- PHX-G512 read-only UI: available
- Managed UI implementation evidence: not applicable

## Implementation boundary

No frontend implementation or business write is authorized until an
independent Coding Authorization is approved.
