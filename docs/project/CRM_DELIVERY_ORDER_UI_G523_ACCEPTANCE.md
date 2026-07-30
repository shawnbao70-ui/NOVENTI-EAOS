# PHX-G523 Acceptance — CRM Delivery Order Read / Release UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_DELIVERY_ORDER_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_DELIVERY_ORDER_G523_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G522 evidence](CRM_QUOTE_ISSUE_UI_G522_ACCEPTANCE.md)

## Accepted Result

**PHX-G523 COMPLETE.**

- Added Smart Terminal Sales-Order-scoped Delivery Order create, detail
  read, and Release.
- Required explicit confirmation for create and Release; Release uses
  `human_confirm: true`, idempotency, and optional approval_ref.
- No tenant Delivery Order collection API was added.
- Permission defaults deny; server remains authoritative.
- Invoice, Return Authorization, and ship deepen remain outside this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g523_crm_delivery_order_ui.py`
- G512–G522 regression contracts
- Focused cumulative result: **61 passed**
- Browser: `phx-g523-delivery-order-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G523**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G523**
- Further Coding / Runtime / Production: **None**
- PHX-G524–G527: **Closed**

## Final Stop

**TRACK-G523 COMPLETE — FINAL STOP TRACK-G523.**
