# Architecture Gate — CRM Business UI Serial U→AB

> **System-generated governance artifact**  
> Product Owner editing is neither required nor permitted.

## Authority and references

- Framework ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- Package ADR: [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)
- Approved Decision Summary:
  [CRM_BUSINESS_UI_SERIAL_DECISION_SUMMARY.md](CRM_BUSINESS_UI_SERIAL_DECISION_SUMMARY.md)
- Approval Record:
  [CRM_BUSINESS_UI_SERIAL_APPROVAL_RECORD.md](CRM_BUSINESS_UI_SERIAL_APPROVAL_RECORD.md)
- Evidence:
  [PHX-G513 Acceptance](CRM_CUSTOMER_CONTACT_UI_G513_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (planning boundary only)**
- Coding Authorization: **None**
- Open Implementation Milestone: **None**

## Generated boundary

### Purpose

Define a strict serial plan for eight CRM commercial-chain UI slices.

### Scope

Opportunity → Requirement → Quote header → Quote lines → Quote convert → Sales
Order read → Sales Order confirm → Customer 360 read-only composition.

### Architecture Boundary

Smart Terminal remains a CRM-owned client of existing APIs. Trusted context,
server Permission, audit, lifecycle, privacy, and concurrency controls remain
authoritative. Each slice must pass an independent Product Gate and Coding
Authorization.

### In Scope

- Eight candidate slices in approved order
- Frontend-only default boundary
- Per-slice contracts and browser evidence after coding approval
- HOLD and serial stop on backend prerequisite gaps
- Candidate final stop TRACK-G521

### Out of Scope

- Backend, persistence, migration, Runtime Manifest, or production changes
- Adjacent package expansion
- External networks, automatic writes, hard delete, permission bypass
- Parallel or skipped milestones

## OD dispositions

| OD | Decision | Generated disposition | Evidence |
|---|---|---|---|
| OD-01 | Independent slice Gates | Accepted | approved Summary |
| OD-02 | Independent Coding Authorization | Accepted; currently None | Approval Record |
| OD-03 | Backend prerequisite gap | HOLD current slice and stop | approved Summary |
| OD-04 | Candidate milestone numbering | Unopened until coding approval | Approval Record |
| OD-05 | Candidate final stop | TRACK-G521 | approved Summary |

## RC attestations

| RC | Control | Generated attestation | Evidence |
|---|---|---|---|
| RC-01 | CRM Package ownership | Pass | ADR-0320 |
| RC-02 | Tenant trusted context | Pass | Summary |
| RC-03 | Permission default-deny | Pass | Summary |
| RC-04 | Audit and concurrency | Pass | Summary |
| RC-05 | Privacy / PII minimization | Pass | Summary |
| RC-06 | No adjacent-domain expansion | Pass | Out of Scope |
| RC-07 | Serial/no-skip discipline | Pass | Summary |
| RC-08 | Gate/coding state separation | Pass | Approval Record |

## Risks

Backend gaps, high-impact transition semantics, Customer 360 privacy expansion,
authorization confusion, and milestone drift remain explicit controls.

## Approval Record

- Product Owner decision: **Approve**
- Decision date: 2026-07-28
- Approval meaning: serial planning boundary only
- Coding Authorization: **None**

## Signature

System-generated projection of the explicit Product Owner `Approve` response.
No manual signature is required.

## Evidence

- PHX-G513 managed Customer/Contact UI: available
- G514–G521 implementation evidence: not applicable

## Implementation boundary

No candidate milestone is opened and no implementation is authorized. The next
valid governance action is the independent G514 Opportunity Managed UI Product
Gate.
