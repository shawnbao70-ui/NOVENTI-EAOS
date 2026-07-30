# PHX-G518 Acceptance — CRM Quote Convert UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Architecture Gate](CRM_QUOTE_CONVERT_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_QUOTE_CONVERT_G518_CODING_AUTHORIZATION_SUMMARY.md)
- [PHX-G517 evidence](CRM_QUOTE_LINES_UI_G517_ACCEPTANCE.md)

## Accepted Result

**PHX-G518 COMPLETE.**

- Added Convert confirmation for issued Quotes.
- Added Conversion detail refresh and Sales Order shell creation from a ready
  Conversion.
- Idempotent Convert returns the existing Conversion without overwrite.
- Permission defaults deny; server remains authoritative.
- Explicit confirmation is required for Convert and SO shell creation.
- Quote Issue, Sales Order Confirm, Delivery, Invoice, and Return Authorization
  remain outside this slice.
- No backend, Repository, Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g518_crm_quote_convert_ui.py`
- G512–G517 regression contracts
- Focused cumulative result: **40 passed**
- Browser: `phx-g518-quote-convert-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G518**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G518**
- Further Coding / Runtime / Production: **None**
- PHX-G519–G525: **Closed**

## Final Stop

**TRACK-G518 COMPLETE — FINAL STOP TRACK-G518.**
