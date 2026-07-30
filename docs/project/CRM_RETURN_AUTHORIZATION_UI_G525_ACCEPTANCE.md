# PHX-G525 Acceptance — CRM Return Authorization Read-only UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_RETURN_AUTHORIZATION_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_RETURN_AUTHORIZATION_G525_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G524 evidence](CRM_AR_INVOICE_UI_G524_ACCEPTANCE.md)

## Accepted Result

**PHX-G525 COMPLETE.**

- Added Smart Terminal Delivery-Order-scoped Return Authorization create and
  detail read (Create gated on shipped Delivery Order).
- Required explicit confirmation, `reason`, and `human_confirm: true` on create;
  optional `invoice_id` when an issued/voided Invoice is selected.
- No tenant Return Authorization collection API was added.
- Permission defaults deny; server remains authoritative.
- Restock, Credit Note, AR Invoice Void, Receipt, GL posting, and Inventory
  ship UI remain outside this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g525_crm_return_authorization_ui.py`
- G512–G524 regression contracts
- Focused cumulative result: **69 passed**
- Browser: `phx-g525-return-authorization-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G525**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G525**
- Further Coding / Runtime / Production: **None**
- PHX-G526–G527: **Closed**

## Final Stop

**TRACK-G525 COMPLETE — FINAL STOP TRACK-G525.**
