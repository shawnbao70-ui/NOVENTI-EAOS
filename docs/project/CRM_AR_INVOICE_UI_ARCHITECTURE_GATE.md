# Architecture Gate — CRM AR Invoice Read / Issue UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_AR_INVOICE_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_AR_INVOICE_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G523 evidence](CRM_DELIVERY_ORDER_UI_G523_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed AR Invoice create/read and Issue UX.

### Scope

Create Invoice shell from released Delivery Order; read detail; Issue with
explicit confirmation, idempotency, optional approval_ref, and refresh.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing
create/get/issue APIs; DO-scoped selection without collection list; no
Void/RA/Receipt/GL posting.

### In Scope

- Existing create/get/issue endpoints
- Selected released Delivery Order from governed G523 surface
- Issue failure handling (403/404/409/422)
- HOLD path if a missing prerequisite is required

### Out of Scope

- Void, RA, Receipt, Finance GL posting
- Ungated backend/persistence/runtime (unless Coding Auth allows list)
- Adjacent packages, production, G525+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing create/get/issue APIs | Accepted |
| OD-02 | Selection model | DO-scoped create+get |
| OD-03 | Issueable status | `draft` only |
| OD-04 | Idempotent Issue | Return existing; no overwrite |
| OD-05 | Missing prerequisite | HOLD G524 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm on Issue | Pass at design level |
| RC-05 | No Void/RA/Receipt/GL expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Missing list, duplicate Issue, Void/GL/Receipt leakage, and cross-tenant
association remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G523 and existing AR Invoice API contracts are available; implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: create/get/issue exist; **no tenant Invoice list** —
selection is DO-scoped (resolved at Coding Authorization).
