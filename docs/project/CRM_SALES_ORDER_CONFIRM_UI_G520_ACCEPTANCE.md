# PHX-G520 Acceptance — CRM Sales Order Confirm UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_SALES_ORDER_CONFIRM_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_SALES_ORDER_CONFIRM_G520_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G519 evidence](CRM_SALES_ORDER_UI_G519_ACCEPTANCE.md)

## Accepted Result

**PHX-G520 COMPLETE.**

- Added Smart Terminal Confirm for selected `created` Sales Orders.
- Required explicit confirmation, `human_confirm: true`, and per-submit
  idempotency; optional approval_ref supported.
- Post-confirm detail and line refresh; lines materialize on Confirm.
- Permission defaults deny; server remains authoritative.
- Delivery, Invoice, Return Authorization, and Quote Issue remain outside
  this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g520_crm_sales_order_confirm_ui.py`
- G512–G519 regression contracts
- Focused cumulative result: **49 passed**
- Browser: `phx-g520-sales-order-confirm-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G520**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G520**
- Further Coding / Runtime / Production: **None**
- PHX-G521–G527: **Closed**

## Final Stop

**TRACK-G520 COMPLETE — FINAL STOP TRACK-G520.**
