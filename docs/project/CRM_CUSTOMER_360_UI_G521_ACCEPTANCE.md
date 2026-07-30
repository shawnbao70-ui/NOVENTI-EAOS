# PHX-G521 Acceptance — CRM Customer 360 Read-only Composition UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_CUSTOMER_360_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_CUSTOMER_360_G521_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G520 evidence](CRM_SALES_ORDER_CONFIRM_UI_G520_ACCEPTANCE.md)

## Accepted Result

**PHX-G521 COMPLETE.**

- Added Smart Terminal Customer 360 read-only composition for the selected
  Customer over existing `GET /v1/crm/customers/{id}/360`.
- Displays commercial_hold, open-order counts, and invoice/receipt/credit
  traces as non-navigating read-only lists.
- Permission defaults deny; server remains authoritative.
- Commercial Hold write, Quote Issue, Delivery, Invoice, and Return
  Authorization remain outside this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g521_crm_customer_360_ui.py`
- G512–G520 regression contracts
- Focused cumulative result: **53 passed**
- Browser: `phx-g521-customer-360-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G521**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G521**
- Further Coding / Runtime / Production: **None**
- PHX-G522–G527: **Closed**

## Final Stop

**TRACK-G521 COMPLETE — FINAL STOP TRACK-G521.**
