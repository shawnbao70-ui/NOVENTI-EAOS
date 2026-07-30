# Architecture Gate — CRM Sales Order Read-only UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_SALES_ORDER_READONLY_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_SALES_ORDER_READONLY_UI_APPROVAL_RECORD.md)
- [PHX-G518 evidence](CRM_QUOTE_CONVERT_UI_G518_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Sales Order read-only UX.

### Scope

Sales Order list/detail and line reads with Permission-aware fail-closed
states. Confirm and fulfillment remain outside.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; server Permission default-deny;
read-only controls; existing get/line APIs plus any accepted list prerequisite.

### In Scope

- Sales Order collection/detail projection
- Selected Sales Order line list
- 403/404 handling
- HOLD when collection capability is missing

### Out of Scope

- Confirm, Delivery, Invoice, Return Auth, Convert expansion
- Ungated backend, persistence, runtime, adjacent packages, production, G520+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing get/line dependency | Accepted |
| OD-02 | Missing collection | HOLD G519 |
| OD-03 | Confirm | Deferred to G520 |
| OD-04 | DTO minimization | Existing closed contracts |
| OD-05 | Writes | None in this slice |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Read-only scope | Pass |
| RC-05 | No Confirm/fulfillment expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Collection gaps, cross-tenant association, authorization confusion, and
Confirm-scope leakage remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G518 and existing get/line APIs are available; implementation evidence is
not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: **Sales Order collection list API missing → HOLD.**
