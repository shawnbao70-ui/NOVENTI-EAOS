# Architecture Gate — CRM AR Invoice Void UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_AR_INVOICE_VOID_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_AR_INVOICE_VOID_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G525 evidence](CRM_RETURN_AUTHORIZATION_UI_G525_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed AR Invoice Void UX for a selected issued Invoice.

### Scope

Void with explicit confirmation, reason, idempotency, and post-void refresh;
no Receipt, GL posting, RA Restock/Credit Note, or Commercial Hold.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing void
API; selection from G524 Invoice surface without collection list; Void
requires `human_confirm: true`, `reason`, and `idempotency_key`; only
`issued` invoices are voidable.

### In Scope

- Existing void endpoint
- Selected issued Invoice from governed G524 surface
- Void failure handling (403/404/409/422)
- HOLD path if a missing prerequisite is required

### Out of Scope

- Receipt, Finance GL posting, RA Restock/Credit Note, Commercial Hold
- Ungated backend/persistence/runtime (unless Coding Auth allows list)
- Adjacent packages, production, G527+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing void API | Accepted |
| OD-02 | Voidable status | `issued` only |
| OD-03 | Idempotent Void | Return existing voided; no overwrite |
| OD-04 | Selection model | G524 DO-scoped Invoice surface |
| OD-05 | Missing prerequisite | HOLD G526 |
| OD-06 | Coding Authorization | Independent; default None |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm on Void | Pass at design level |
| RC-05 | No Receipt/GL/RA write/Hold expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

GL/Receipt/Hold leakage, void without confirmation, and cross-tenant
association remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G525 and existing AR Invoice void API contracts are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: void exists; **no tenant Invoice list** — selection is
G524 DO-scoped (resolved at Coding Authorization).
