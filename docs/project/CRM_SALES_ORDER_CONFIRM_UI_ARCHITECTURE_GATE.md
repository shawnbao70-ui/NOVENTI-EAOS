# Architecture Gate — CRM Sales Order Confirm UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_SALES_ORDER_CONFIRM_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_SALES_ORDER_CONFIRM_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G519 evidence](CRM_SALES_ORDER_UI_G519_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Sales Order Confirm UX.

### Scope

Confirm for selected `created` Sales Orders with explicit confirmation,
idempotency, optional approval_ref, and post-confirm refresh.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing
Confirm API; high-impact explicit confirmation; no Delivery/Invoice/RA/Issue.

### In Scope

- Existing `POST /v1/crm/sales-orders/{id}/confirm`
- Selected Sales Order from governed G519 collection
- Line refresh after Confirm
- 403/404/409/422 and approval/commercial-hold failure handling

### Out of Scope

- Delivery, Invoice, Return Auth, Quote Issue
- Ungated backend, persistence, runtime, adjacent packages, production, G521+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing Confirm API | Accepted |
| OD-02 | Confirmable status | `created` only |
| OD-03 | Idempotent Confirm | Return existing; no overwrite |
| OD-04 | approval_ref | Required only when policy demands |
| OD-05 | Missing prerequisite | HOLD G520 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm | Pass at design level |
| RC-05 | No Delivery/Invoice expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Duplicate Confirm, approval-gate unavailability, commercial-hold blocks,
cross-tenant association, and Delivery/Invoice leakage remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G519 and existing Confirm API contracts are available; implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: Confirm API and G519 SO collection exist; **no HOLD**.
