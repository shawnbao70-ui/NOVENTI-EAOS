# PHX-G513 Acceptance — CRM Customer + Contact Managed UI

> **System-generated governance artifact** under ADR-0321 Phoenix Gate
> Framework.

## References

- ADR:
  [ADR-0321 Phoenix Gate Framework](../decisions/ADR-0321-phoenix-gate-framework.md)
- Approved Decision Summary:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_DECISION_SUMMARY.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_DECISION_SUMMARY.md)
- Architecture Gate:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_ARCHITECTURE_GATE.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_ARCHITECTURE_GATE.md)
- Gate Acceptance:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_ACCEPTANCE.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_ACCEPTANCE.md)
- Independent Coding Authorization:
  [CRM_CUSTOMER_CONTACT_MANAGED_UI_CODING_AUTHORIZATION_SUMMARY.md](CRM_CUSTOMER_CONTACT_MANAGED_UI_CODING_AUTHORIZATION_SUMMARY.md)

## Accepted Result

Milestone **PHX-G513** is complete.

- Smart Terminal exposes Customer and Contact create, edit, and archive forms.
- Write controls derive only from the current subject's effective CRM grants;
  missing, empty, denied, or unavailable projection hides every write control.
- Server Permission remains authoritative for every request.
- Tenant and actor identifiers are never accepted from managed form bodies.
- Update and archive send the selected record's `expected_version`.
- `409` stops without retry or overwrite and refreshes the governed view.
- Archive requires a reason plus explicit secondary confirmation.
- Contact email and phone remain optional and are never inferred.
- Import, merge, hard delete, bulk/automatic write, and commercial hold remain
  outside the UI.
- No API, Service, Repository, Database, Alembic, or Runtime Manifest change.

## Evidence

- Contract:
  `tests/contracts/test_api_gateway_g513_crm_managed_ui.py`
- Regression:
  `tests/contracts/test_api_gateway_g512_crm_customer_contact_ui.py`
- Focused result: **12 passed**
- Browser: local Smart Terminal `#crm` verified the fail-closed locked state with
  the gateway CRM service unavailable; no write affordance or mutation request
  was exposed.
- Visual evidence: `phx-g513-crm-workspace-final.png` (session screenshot)

## Risk-Control Attestations

- RC-PERMISSION: effective grants control affordance only; server checks remain
  authoritative and default deny.
- RC-TENANT: trusted context only; no tenant body elevation.
- RC-PII: optional Contact PII is explicit and absent from collection items.
- RC-CONCURRENCY: optimistic version supplied; conflicts do not auto-overwrite.
- RC-LIFECYCLE: archive only; no hard delete.
- RC-SCOPE: frontend and evidence only; backend/runtime boundaries unchanged.

## Approval Record

- Product Owner design decision: **Approve**
- Product Owner Coding Authorization: **Approve**
- Approval date: **2026-07-28**
- Milestone: **PHX-G513**

## Signature

- Product Owner: approved in the authoritative conversation
- Generator: Cursor agent, system-generated from approved summaries
- Generated: 2026-07-28

## Authorization State

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gate Accepted: **Yes**
- Coding Authorization: **Consumed by PHX-G513**
- Further Coding Authorization: **None**
- Runtime Manifest Authorization: **None**
- Production Authorization: **None**

## Final Stop

**TRACK-G513 COMPLETE — FINAL STOP TRACK-G513.**
