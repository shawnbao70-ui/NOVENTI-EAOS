# Architecture Gate — CRM Return Authorization Read-only UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_RETURN_AUTHORIZATION_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_RETURN_AUTHORIZATION_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G524 evidence](CRM_AR_INVOICE_UI_G524_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Return Authorization create/read display UX without Restock
or Credit Note writes.

### Scope

Create RA shell from selected Delivery Order; read detail and refresh; no
Restock, Credit Note, Invoice Void, Receipt, or GL posting.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing
create/get APIs; DO-scoped selection without collection list; create requires
`human_confirm: true`, `reason`, and `idempotency_key` (optional
`invoice_id`); Restock/Credit Note remain closed.

### In Scope

- Existing create/get endpoints
- Selected Delivery Order from governed G523 surface (and Invoice association
  where optional `invoice_id` applies)
- Create failure handling (403/404/409/422)
- HOLD path if a missing prerequisite is required

### Out of Scope

- Restock, Credit Note, AR Invoice Void, Receipt, Finance GL posting
- Ungated backend/persistence/runtime (unless Coding Auth allows list)
- Adjacent packages, production, G526+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing create/get APIs | Accepted |
| OD-02 | Selection model | DO-scoped create+get |
| OD-03 | Read-only meaning | Create shell for selection; Restock/Credit Note excluded |
| OD-04 | Missing prerequisite | HOLD G525 |
| OD-05 | Coding Authorization | Independent; default None |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm on Create | Pass at design level |
| RC-05 | No Restock/Credit Note/Void/GL expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Missing list, Restock/Credit Note/Void leakage, create confirmation bypass,
and cross-tenant association remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G524 and existing Return Authorization API contracts are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: create/get exist; **no tenant RA list** — selection is
DO-scoped (resolved at Coding Authorization).
