# Architecture Gate — CRM Requirement Managed UI

> **System-generated governance artifact**

## Authority and references

- ADR-0321 Phoenix Gate Framework
- [ADR-0323 Requirement boundary](../decisions/ADR-0323-crm-requirement-product-boundary.md)
- [Approved Summary](CRM_REQUIREMENT_MANAGED_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_REQUIREMENT_MANAGED_UI_APPROVAL_RECORD.md)
- [PHX-G514 evidence](CRM_OPPORTUNITY_UI_G514_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Requirement list/detail and managed-record UX.

### Scope

Frontend-only Requirement collection, detail, create, edit, archive, and
governed Opportunity association.

### Architecture Boundary

CRM-owned UI; trusted Tenant/actor context; server Permission default-deny;
optimistic concurrency; archive instead of hard delete.

### In Scope

- Requirement list/detail/forms
- Governed Opportunity association
- Permission-aware controls
- Archive reason and confirmation
- 403/404/409/422 handling
- Frontend contracts and browser evidence

### Out of Scope

- Ungated backend or persistence expansion
- Quote and downstream slices
- Adjacent packages, automatic writes, runtime, production

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Initial API dependency | Existing interfaces only |
| OD-02 | Missing collection query | HOLD G515 |
| OD-03 | Opportunity association | Governed records only |
| OD-04 | Conflict behavior | Stop and refresh; no overwrite |
| OD-05 | Coding separation | Remains None |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Audit/concurrency | Pass |
| RC-05 | No hard delete | Pass |
| RC-06 | Serial stop | Pass |
| RC-07 | Coding separation | Pass |

## Risks

Collection gaps, cross-tenant association, authorization confusion, and stale
versions remain constrained by the approved Summary.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

ADR-0323 and PHX-G514 are available. Implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized until a separate Coding
Authorization is approved.
