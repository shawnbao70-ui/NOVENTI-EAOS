# Architecture Gate — CRM Delivery Order Read / Release UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_DELIVERY_ORDER_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_DELIVERY_ORDER_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G522 evidence](CRM_QUOTE_ISSUE_UI_G522_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Delivery Order create/read and Release UX.

### Scope

Create Delivery Order shell from confirmed Sales Order; read detail; Release
with explicit confirmation, idempotency, optional approval_ref, and refresh.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing
create/get/release APIs; SO-scoped selection without collection list, or HOLD
for list prerequisite; no Invoice/RA/ship deepen.

### In Scope

- Existing create/get/release endpoints
- Selected confirmed Sales Order from governed G519/G520 surfaces
- Release failure handling (403/404/409/422)
- HOLD path if list prerequisite is required

### Out of Scope

- Invoice, RA, inventory ship deepen, Quote Issue changes
- Ungated backend/persistence/runtime (unless Coding Auth allows list)
- Adjacent packages, production, G524+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing create/get/release APIs | Accepted |
| OD-02 | Selection model | SO-scoped create+get, or HOLD for list |
| OD-03 | Releasable status | Only releasable statuses expose Release |
| OD-04 | Idempotent Release | Return existing; no overwrite |
| OD-05 | Missing prerequisite | HOLD G523 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm on Release | Pass at design level |
| RC-05 | No Invoice/RA/ship expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Missing list HOLD, duplicate Release, Invoice/Ship leakage, and cross-tenant
association remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G522 and existing Delivery Order API contracts are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: create/get/release exist; **no tenant DO list** —
selection is SO-scoped or HOLD (resolved at Coding Authorization).
