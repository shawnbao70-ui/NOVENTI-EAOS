# Architecture Gate — CRM Customer + Contact UI

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Package ADR: [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)
- Approved Decision Summary:
  [CRM_CUSTOMER_CONTACT_UI_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_UI_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_CUSTOMER_CONTACT_UI_APPROVAL_RECORD.md](CRM_CUSTOMER_CONTACT_UI_APPROVAL_RECORD.md)
- Evidence:
  [CRM Customer + Contact Architecture Gate](CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md) ·
  [CRM Customer + Contact Acceptance](CRM_CUSTOMER_CONTACT_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design boundary only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Create a tenant-safe, permission-aware, read-only UI boundary for CRM Customer
and Contact discovery and detail presentation.

### Scope

The accepted first slice contains CRM navigation, Customer and Contact
list/detail presentation, and complete loading, empty, denied, and error
states. It may consume only compatible, already-governed query interfaces.

### Architecture Boundary

The UI remains inside the CRM Business Package. Tenant and actor authority
come from trusted execution context. The frontend may project server
authorization results but cannot become an authorization truth source.

### In Scope

- CRM navigation and page composition
- Customer and Contact read-only list/detail surfaces
- Permission-aware and failure-state presentation
- Read-only audit correlation presentation when already available

### Out of Scope

- Frontend implementation before independent Coding Authorization
- New or modified CRUD, API, Repository, Database, or Alembic behavior
- Customer/Contact writes and actionable write controls
- Import, merge, Customer 360, Finance, Workflow, Brain, or Twin
- Runtime Manifest changes and automatic business writes

## OD dispositions

| OD | Decision from approved Summary | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | First slice is read-only | Accepted | approved Summary |
| OD-02 | Reuse governed query interfaces only when compatible | Accepted with fail-closed condition | approved Summary |
| OD-03 | Disabled placeholder versus omission | Deferred; no actionable write control allowed | Out of Scope |

The Product Owner does not edit this table.

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | Package / Kernel boundary | Pass | ADR-0320 / approved Summary |
| RC-02 | Tenant isolation | Pass — trusted context required | ADR-0320 |
| RC-03 | Permission default-deny | Pass — server remains authority | ADR-0320 |
| RC-04 | No backend or runtime expansion | Pass | approved Out of Scope |
| RC-05 | No business writes | Pass | approved Out of Scope |
| RC-06 | Coding state separation | Pass — authorization remains None | Approval Record |

Missing implementation evidence is not inferred as capability.

## Risks

- Existing query interfaces may not satisfy desired presentation data.
- UI visibility controls could be mistaken for authorization.
- A design-accepted UI could be mistaken for implementation authority.

These risks are constrained by fail-closed interface reuse, server-side
Permission authority, and independent Coding Authorization.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approved Summary:
  [CRM_CUSTOMER_CONTACT_UI_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_UI_DECISION_SUMMARY.md)
- Approval meaning: design boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- ADR-0320 CRM Customer + Contact product boundary: available
- Existing CRM Architecture Gate and Acceptance: available
- Query-interface compatibility: not assessed by this design Gate
- UI implementation evidence: not applicable; coding is unauthorized

## Implementation boundary

No frontend implementation, CRUD, API, Repository, Database, Alembic, Runtime
Manifest, implementation milestone, or business-write work is authorized.
