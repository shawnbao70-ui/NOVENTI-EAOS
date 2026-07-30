# PHX-G514 Acceptance — CRM Opportunity Managed UI

> **System-generated governance artifact** under ADR-0321 Phoenix Gate
> Framework.

## References

- ADR: [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- UI Decision Summary:
  [CRM_OPPORTUNITY_MANAGED_UI_DECISION_SUMMARY.md](CRM_OPPORTUNITY_MANAGED_UI_DECISION_SUMMARY.md)
- UI Gate:
  [CRM_OPPORTUNITY_MANAGED_UI_ARCHITECTURE_GATE.md](CRM_OPPORTUNITY_MANAGED_UI_ARCHITECTURE_GATE.md)
- List-query Decision Summary:
  [CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md](CRM_OPPORTUNITY_LIST_QUERY_DECISION_SUMMARY.md)
- List-query Gate:
  [CRM_OPPORTUNITY_LIST_QUERY_ARCHITECTURE_GATE.md](CRM_OPPORTUNITY_LIST_QUERY_ARCHITECTURE_GATE.md)
- Coding Authorization:
  [CRM_OPPORTUNITY_G514_CODING_AUTHORIZATION_SUMMARY.md](CRM_OPPORTUNITY_G514_CODING_AUTHORIZATION_SUMMARY.md)
- HOLD:
  [CRM_OPPORTUNITY_UI_G514_HOLD.md](CRM_OPPORTUNITY_UI_G514_HOLD.md)

## Accepted Result

Milestone **PHX-G514** is complete.

- Added tenant-scoped active Opportunity collection reads with opaque bounded
  cursor pagination.
- Added closed minimal Opportunity list DTO/OpenAPI contracts.
- In-memory and SQLAlchemy repositories use stable `updated_at + id` ordering.
- Smart Terminal exposes Opportunity list/detail/create/edit/archive.
- Customer association choices come from governed Customer collection data.
- Write controls derive only from effective Opportunity grants.
- Server Permission remains authoritative; missing projection hides writes.
- Update and archive carry `expected_version`; 409 never retries or overwrites.
- Archive requires a reason and explicit confirmation.
- No Database schema, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- Contract:
  `tests/contracts/test_api_gateway_g514_crm_opportunity_ui.py`
- Regression:
  `test_api_gateway_g512_crm_customer_contact_ui.py` and
  `test_api_gateway_g513_crm_managed_ui.py`
- Focused result: **18 passed**
- Browser: local Smart Terminal `#crm` verified Opportunity fail-closed behavior
  with CRM service unavailable and no write affordance exposed.
- Visual evidence: `phx-g514-opportunity-workspace.png`

## Risk-Control Attestations

- RC-TENANT: trusted context and repository tenant filters.
- RC-PERMISSION: default-deny list/write service checks; UI only projects grants.
- RC-PAGINATION: bounded cursor and stable ordering.
- RC-CONCURRENCY: expected version; no automatic overwrite.
- RC-LIFECYCLE: archive only; no hard delete.
- RC-SCOPE: no adjacent package, schema, runtime, or production expansion.

## Approval Record

- Product Owner design decisions: **Approve**
- Product Owner Coding Authorization: **Approve**
- Approval date: **2026-07-28**
- Milestone: **PHX-G514**

## Signature

- Product Owner: approved in the authoritative conversation
- Generator: Cursor agent, system-generated from approved summaries
- Generated: 2026-07-28

## Authorization State

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gates Accepted: **Yes**
- Coding Authorization: **Consumed by PHX-G514**
- Further Coding Authorization: **None**
- Runtime Manifest Authorization: **None**
- Production Authorization: **None**
- PHX-G515–G521: **Closed**

## Final Stop

**TRACK-G514 COMPLETE — FINAL STOP TRACK-G514.**
