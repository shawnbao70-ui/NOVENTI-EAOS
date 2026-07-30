# Architecture Gate — CRM Quote Issue UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [Approved Summary](CRM_QUOTE_ISSUE_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_QUOTE_ISSUE_UI_APPROVAL_RECORD.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G521 evidence](CRM_CUSTOMER_360_UI_G521_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Quote Issue UX for draft Quotes.

### Scope

Issue for selected `draft` Quotes with explicit confirmation, idempotency,
optional approval_ref, and post-issue detail refresh.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; Permission default-deny; existing Issue
API; high-impact explicit confirmation; no Convert/Confirm/Delivery/Invoice/
RA/Hold expansion.

### In Scope

- Existing `POST /v1/crm/quotes/{id}/issue`
- Selected Quote from governed G516 collection
- Post-issue Quote detail refresh
- 403/404/409/422 and approval/commercial-hold failure handling

### Out of Scope

- Convert behavior changes, Confirm, Delivery, Invoice, RA, Hold write
- Ungated backend, persistence, runtime, adjacent packages, production, G523+

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing Issue API | Accepted |
| OD-02 | Issueable status | `draft` only |
| OD-03 | Idempotent Issue | Return existing; no overwrite |
| OD-04 | approval_ref | Required only when policy demands |
| OD-05 | Missing prerequisite | HOLD G522 |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Explicit human_confirm | Pass at design level |
| RC-05 | No Convert/Confirm/Delivery expansion | Pass |
| RC-06 | Coding separation | Pass |

## Risks

Duplicate Issue, approval-gate unavailability, commercial-hold blocks, and
Convert/Confirm/Delivery leakage remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

PHX-G521 and existing Quote Issue API contracts are available;
implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
Prerequisite check: Issue API and G516 Quote collection exist; **no HOLD**.
