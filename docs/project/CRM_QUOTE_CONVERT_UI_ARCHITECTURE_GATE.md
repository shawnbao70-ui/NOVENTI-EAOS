# Architecture Gate — CRM Quote Convert UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Approved Summary](CRM_QUOTE_CONVERT_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_QUOTE_CONVERT_UI_APPROVAL_RECORD.md)
- [PHX-G517 evidence](CRM_QUOTE_LINES_UI_G517_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Quote Convert UX, including conversion result and Sales Order
shell creation from a ready conversion.

### Scope

Issued Quote selection; convert with idempotency and optional FX/approval_ref;
conversion detail; create SO shell; Permission-aware fail-closed controls.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; server Permission default-deny;
existing Convert/Conversion/create-SO APIs; high-impact explicit confirmation;
no Confirm/Issue/Delivery/Invoice/RA expansion.

### In Scope

- Existing `POST /v1/crm/quotes/{id}/convert`
- Existing `GET /v1/crm/conversions/{id}`
- Existing `POST /v1/crm/conversions/{id}/sales-order`
- Issued Quote parent selection from governed Quote list
- 403/404/409/422 and approval-gate failure handling

### Out of Scope

- Quote Issue UI, SO Confirm, Delivery, Invoice, Return Auth
- Ungated backend, persistence, runtime, adjacent packages, production, G519+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing API dependency | Accepted |
| OD-02 | Convertible Quotes | Issued only |
| OD-03 | Idempotent convert | Return existing; no overwrite |
| OD-04 | approval_ref | Required only when policy demands |
| OD-05 | SO create from conversion | In G518; Confirm remains G520 |
| OD-06 | Missing prerequisite | HOLD G518 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Issued-quote precondition | Pass at design level |
| RC-05 | Idempotency / conflict | Pass |
| RC-06 | No Confirm/Issue expansion | Pass |
| RC-07 | Coding separation | Pass |

## Risks

Duplicate convert, approval-gate unavailability, FX validation, cross-tenant
association, and accidental Confirm/Issue scope remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

Existing Convert API contracts and PHX-G517 are available; implementation
evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: Convert / Conversion / create-SO APIs exist; no HOLD.
