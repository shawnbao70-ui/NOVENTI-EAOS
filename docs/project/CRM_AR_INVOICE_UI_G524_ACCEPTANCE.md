# PHX-G524 Acceptance — CRM AR Invoice Read / Issue UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_AR_INVOICE_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_AR_INVOICE_G524_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G523 evidence](CRM_DELIVERY_ORDER_UI_G523_ACCEPTANCE.md)

## Accepted Result

**PHX-G524 COMPLETE.**

- Added Smart Terminal Delivery-Order-scoped AR Invoice create, detail
  read, and Issue.
- Required explicit confirmation for create and Issue; Issue uses
  `human_confirm: true` and idempotency only (no approval_ref).
- No tenant AR Invoice collection API was added.
- Permission defaults deny; server remains authoritative.
- Void, Return Authorization, Receipt, and GL posting remain outside this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g524_crm_ar_invoice_ui.py`
- G512–G523 regression contracts
- Focused cumulative result: **65 passed**
- Browser: `phx-g524-ar-invoice-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G524**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G524**
- Further Coding / Runtime / Production: **None**
- PHX-G525–G527: **Closed**

## Final Stop

**TRACK-G524 COMPLETE — FINAL STOP TRACK-G524.**
