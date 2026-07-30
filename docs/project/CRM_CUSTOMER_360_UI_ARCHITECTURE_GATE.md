# Architecture Gate — CRM Customer 360 Read-only Composition UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_CUSTOMER_360_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_CUSTOMER_360_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G520 evidence](CRM_SALES_ORDER_CONFIRM_UI_G520_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Customer 360 read-only composition UX.

### Scope

Read-only panel for the selected Customer using the existing `/360`
projection, including commercial_hold, open-order counts, and
invoice/receipt/credit-note traces.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing
Customer 360 API; no Hold write; no Quote Issue / Delivery / Invoice / RA.

### In Scope

- Existing `GET /v1/crm/customers/{id}/360`
- Selected Customer from governed CRM Customer surface
- Read-only composition rendering and fail-closed states
- 403/404/422 failure handling

### Out of Scope

- Commercial Hold write, Issue, Delivery, Invoice, Return Auth
- Ungated backend, persistence, runtime, adjacent packages, production, G522+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing `/360` API | Accepted as sole dependency |
| OD-02 | Selection required | No Customer → no 360 load |
| OD-03 | Traces | Read-only; no write navigation |
| OD-04 | Missing prerequisite | HOLD G521 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Read-only composition | Pass at design level |
| RC-05 | No Hold/Issue/Delivery expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

PII/financial-trace creep, accidental Hold/Issue opening, and Finance
scope drift remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G520 and existing Customer 360 API contracts are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: Customer 360 API exists; **no HOLD**.
