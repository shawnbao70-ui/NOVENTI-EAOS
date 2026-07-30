# Architecture Gate — CRM Opportunity Managed UI

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Approved serial plan:
  [CRM_BUSINESS_UI_SERIAL_ACCEPTANCE.md](CRM_BUSINESS_UI_SERIAL_ACCEPTANCE.md)
- Approved Decision Summary:
  [CRM_OPPORTUNITY_MANAGED_UI_DECISION_SUMMARY.md](CRM_OPPORTUNITY_MANAGED_UI_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_OPPORTUNITY_MANAGED_UI_APPROVAL_RECORD.md](CRM_OPPORTUNITY_MANAGED_UI_APPROVAL_RECORD.md)
- Evidence:
  [PHX-G513 Acceptance](CRM_CUSTOMER_CONTACT_UI_G513_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Opportunity list/detail and managed-record UX over existing CRM
interfaces.

### Scope

Frontend-only Opportunity collection, detail, create, edit, and archive flows,
including governed Customer association and failure states.

### Architecture Boundary

CRM owns the UI. Trusted context supplies Tenant and actor identity.
Server-side Permission remains authoritative. Update/archive carry
`expected_version`; archive replaces hard delete.

### In Scope

- Opportunity list/detail and managed forms
- Customer association from governed records
- Permission-aware affordances
- Archive confirmation and reason
- 403/404/409/422 handling
- Frontend contracts and browser evidence

### Out of Scope

- Backend/API/Repository/Database/Alembic changes
- Stage automation, scoring, forecasting, import, merge, bulk writes
- Requirement and downstream commercial slices
- Adjacent packages, Runtime Manifest, production

## OD dispositions

| OD | Decision | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Existing API dependency | Accepted | approved Summary |
| OD-02 | Missing backend capability | HOLD G514 and stop | approved Summary |
| OD-03 | Permission projection unavailable | Hide write controls | approved Summary |
| OD-04 | 409 behavior | Stop and refresh; no overwrite | approved Summary |
| OD-05 | Coding separation | Accepted; remains None | Approval Record |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | CRM ownership / Kernel boundary | Pass | Summary |
| RC-02 | Tenant trusted context | Pass | Summary |
| RC-03 | Permission default-deny | Pass | Summary |
| RC-04 | Audit and optimistic concurrency | Pass | Summary |
| RC-05 | Archive, no hard delete | Pass | Summary |
| RC-06 | No backend/runtime expansion | Pass | Out of Scope |
| RC-07 | Serial stop discipline | Pass | serial plan |
| RC-08 | Coding state separation | Pass | Approval Record |

## Risks

Collection-query gaps, tenant association errors, authorization confusion,
concurrency conflicts, and production-status confusion remain controlled by the
accepted boundary.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approval meaning: design boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- CRM serial plan and PHX-G513 baseline: available
- Opportunity UI implementation evidence: not applicable

## Implementation boundary

No frontend implementation or candidate milestone is authorized until an
independent PHX-G514 Coding Authorization is approved.
