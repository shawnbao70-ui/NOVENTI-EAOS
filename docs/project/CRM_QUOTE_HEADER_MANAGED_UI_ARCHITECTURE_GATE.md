# Architecture Gate — CRM Quote Header Managed UI

> **System-generated governance artifact**

## Authority and references

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Approved Summary](CRM_QUOTE_HEADER_MANAGED_UI_DECISION_SUMMARY.md)
- [Approval Record](CRM_QUOTE_HEADER_MANAGED_UI_APPROVAL_RECORD.md)
- [PHX-G515 evidence](CRM_REQUIREMENT_UI_G515_ACCEPTANCE.md)

## Status

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate: **Accepted (design only)**
- Coding Authorization: **None**
- Implementation Milestone: **None**

## Generated boundary

### Purpose

Define governed Quote header management UX.

### Scope

Quote list/detail/create/edit/archive with Requirement association, currency,
notes, failure states, and Permission-aware controls.

### Architecture Boundary

CRM-owned UI; trusted Tenant context; server Permission default-deny;
optimistic concurrency; archive-only lifecycle.

### In Scope

- Quote header collection/detail/forms
- Governed Requirement association
- Currency/notes validation
- Archive confirmation
- 403/404/409/422 handling

### Out of Scope

- Lines, Issue, Convert, approvals, pricing automation
- Ungated backend, persistence, runtime, adjacent packages, production

## OD dispositions

| OD | Decision | Disposition |
|---|---|---|
| OD-01 | Existing API dependency | Accepted |
| OD-02 | Missing collection | HOLD G516 |
| OD-03 | Requirement association | Governed records |
| OD-04 | Currency | Existing 3-character contract |
| OD-05 | Conflict | Stop/refresh; no overwrite |

## RC attestations

| RC | Control | Result |
|---|---|---|
| RC-01 | CRM/Kernel boundary | Pass |
| RC-02 | Tenant isolation | Pass |
| RC-03 | Permission default-deny | Pass |
| RC-04 | Currency/association validation | Pass at design level |
| RC-05 | Optimistic concurrency | Pass |
| RC-06 | No lines/issue/convert expansion | Pass |
| RC-07 | Coding separation | Pass |

## Risks

Collection gaps, currency validation, cross-tenant association, authorization
confusion, and stale versions remain explicit.

## Approval Record

- Product Owner: **Approve**
- Date: 2026-07-29
- Coding Authorization: **None**

## Signature

System-generated from the explicit Product Owner decision.

## Evidence

ADR-0324 and PHX-G515 are available; implementation evidence is not inferred.

## Implementation boundary

No implementation or milestone is authorized.
