# Architecture Gate — CRM Business UI Serial AK→AR

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_BUSINESS_UI_SERIAL_AK_AR_DECISION_SUMMARY.md)
- [Approval Record](CRM_BUSINESS_UI_SERIAL_AK_AR_APPROVAL_RECORD.md)
- [PHX-G519 evidence](CRM_SALES_ORDER_UI_G519_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design plan only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define eight serial CRM UI design slices after TRACK-G519.

### Scope

Sales Order confirm → Customer 360 → Quote Issue → Delivery Order →
AR Invoice issue → Return Authorization → AR Invoice void →
Customer commercial hold.

### Architecture Boundary

CRM-owned Smart Terminal UI; trusted Tenant context; Permission default-deny;
existing APIs; contiguous PHX-G520–G527; one open milestone at a time;
high-impact writes require explicit confirmation. Finance GL / Brain / Twin
remain closed.

### In Scope

- Independent per-slice Decision Summaries and Gates
- Frontend contracts and browser evidence after Coding Authorization
- HOLD on missing prerequisites
- Absorption of remaining closed AC→AJ candidates G520–G525

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
| OD-06 | Final stop | TRACK-G527 |
| OD-07 | Relation to AC→AJ | Historical; AK→AR is active plan from tip G519 |

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

PHX-G519 and prior serial evidence are available; AK→AR implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized by this Gate.
