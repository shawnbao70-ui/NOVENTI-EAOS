# PHX-G515 Acceptance — CRM Requirement Managed UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0323](../decisions/ADR-0323-crm-requirement-product-boundary.md)
- [UI Summary](CRM_REQUIREMENT_MANAGED_UI_DECISION_SUMMARY.md)
- [UI Gate](CRM_REQUIREMENT_MANAGED_UI_ARCHITECTURE_GATE.md)
- [List Summary](CRM_REQUIREMENT_LIST_QUERY_DECISION_SUMMARY.md)
- [List Gate](CRM_REQUIREMENT_LIST_QUERY_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_REQUIREMENT_G515_CODING_AUTHORIZATION_SUMMARY.md)
- [HOLD](CRM_REQUIREMENT_UI_G515_HOLD.md)

## Accepted Result

**PHX-G515 COMPLETE.**

- Added tenant-scoped active Requirement collection reads.
- Added bounded opaque-cursor pagination and closed minimal DTOs.
- In-memory and SQLAlchemy repositories use stable `updated_at + id`.
- Added Requirement list/detail/create/edit/archive UI.
- Opportunity association comes from governed Opportunity collection data.
- Effective grants project controls; server Permission remains authoritative.
- Update/archive use `expected_version`; conflicts never auto-overwrite.
- Archive requires reason and confirmation.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g515_crm_requirement_ui.py`
- G512–G514 regression contracts
- Focused result: **24 passed**
- Browser fail-closed verification: `phx-g515-requirement-workspace.png`

## RC attestations

- Tenant isolation, Permission default-deny, bounded pagination, governed
  association, optimistic concurrency, archive-only lifecycle, and serial scope:
  **Pass**.

## Approval Record

- Product Owner design: **Approve**
- Product Owner Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G515**

## Signature

System-generated from the authoritative Product Owner decisions.

## Authorization State

- Accepted Knowledge: **Independent / unchanged**
- Architecture Gates: **Accepted**
- Coding Authorization: **Consumed by PHX-G515**
- Further Coding Authorization: **None**
- Runtime Manifest / Production: **None**
- PHX-G516–G521: **Closed**

## Final Stop

**TRACK-G515 COMPLETE — FINAL STOP TRACK-G515.**
