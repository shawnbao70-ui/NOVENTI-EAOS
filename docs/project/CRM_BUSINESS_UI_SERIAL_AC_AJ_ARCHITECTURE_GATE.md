# Architecture Gate — CRM Business UI Serial AC→AJ

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_BUSINESS_UI_SERIAL_AC_AJ_DECISION_SUMMARY.md)
- [Approval Record](CRM_BUSINESS_UI_SERIAL_AC_AJ_APPROVAL_RECORD.md)
- [PHX-G517 evidence](CRM_QUOTE_LINES_UI_G517_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design plan only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define eight serial CRM UI design slices after TRACK-G517.

### Scope

Quote Convert → Sales Order read → Sales Order confirm → Customer 360 →
Quote Issue → Delivery Order → AR Invoice → Return Authorization.

### Architecture Boundary

CRM-owned Smart Terminal UI; trusted Tenant context; Permission default-deny;
existing APIs; contiguous PHX-G518–G525; one open milestone at a time;
high-impact writes require explicit confirmation.

### In Scope

- Independent per-slice Decision Summaries and Gates
- Frontend contracts and browser evidence after Coding Authorization
- HOLD on missing prerequisites

### Out of Scope

- Finance GL / Brain / Twin / PSP / production
- Parallel milestones
- Coding Authorization for any slice

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Per-slice Decision Summary | Required |
| OD-02 | Coding Authorization | Independent; default None |
| OD-03 | Missing prerequisite | HOLD current slice; stop queue |
| OD-04 | Milestone numbers | Unopened until Coding Authorization |
| OD-05 | High-impact transitions | Explicit confirmation + existing policy contracts |
| OD-06 | Final stop | TRACK-G525 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Contiguous serial PHX-G | Pass |
| RC-05 | No Finance/Brain/Twin self-open | Pass |
| RC-06 | Coding separation | Pass |
| RC-07 | No parallel second milestone | Pass |

## Risks

API gaps, authority confusion, high-impact transitions, PII/Finance scope
creep, and numbering drift remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G517 and prior serial evidence are available; AC→AJ implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized by this Gate.
