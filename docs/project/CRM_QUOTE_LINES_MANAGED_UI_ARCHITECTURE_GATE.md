# Architecture Gate — CRM Quote Lines Managed UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Approved Summary](CRM_QUOTE_LINES_MANAGED_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_QUOTE_LINES_MANAGED_UI_APPROVAL_RECORD.md)
- [PHX-G516 evidence](CRM_QUOTE_HEADER_UI_G516_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Quote Line management UX.

### Scope

Quote Line list/detail/create/edit/archive under the selected Quote Header, with
decimal fields, calculated amount, failure states, and Permission-aware
controls.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; selected Quote Header as governed parent;
server Permission default-deny; optimistic concurrency; archive-only lifecycle.

### In Scope

- Existing Quote Line collection/detail/write endpoints
- Description, quantity, unit price, calculated amount, and line status
- Parent Quote association and archive confirmation
- 403/404/409/422 handling

### Out of Scope

- Issue, Convert, approvals, pricing automation, discounts, or taxes
- Backend, persistence, runtime, adjacent packages, production, or G518+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing API dependency | Accepted |
| OD-02 | Parent association | Selected governed Quote Header |
| OD-03 | Quantity precision | Existing three-decimal contract |
| OD-04 | Unit-price precision | Existing two-decimal contract |
| OD-05 | Amount ownership | Server-calculated/read-only |
| OD-06 | Conflict | Stop/refresh; no overwrite |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant and parent isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Decimal validation | Pass at design level |
| RC-05 | Optimistic concurrency | Pass |
| RC-06 | No Issue/Convert expansion | Pass |
| RC-07 | Coding separation | Pass |

## Risks

Decimal precision, stale parent selection, cross-tenant association,
authorization confusion, and stale versions remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

ADR-0324, existing Quote Line API contracts, and PHX-G516 are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
