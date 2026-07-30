# PHX-G522 Acceptance — CRM Quote Issue UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [UI Gate](CRM_QUOTE_ISSUE_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_QUOTE_ISSUE_G522_CODING_AUTHORIZATION_SUMMARY.md)
- [Serial plan AK→AR](CRM_BUSINESS_UI_SERIAL_AK_AR_ACCEPTANCE.md)
- [PHX-G521 evidence](CRM_CUSTOMER_360_UI_G521_ACCEPTANCE.md)

## Accepted Result

**PHX-G522 COMPLETE.**

- Added Smart Terminal Issue for selected `draft` Quotes.
- Required explicit confirmation, `human_confirm: true`, and per-submit
  idempotency; optional approval_ref supported.
- Post-issue Quote detail refresh.
- Permission defaults deny; server remains authoritative.
- Convert behavior, Confirm, Delivery, Invoice, RA, and Commercial Hold
  remain outside this slice.
- No Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g522_crm_quote_issue_ui.py`
- G512–G521 regression contracts
- Focused cumulative result: **57 passed**
- Browser: `phx-g522-quote-issue-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G522**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G522**
- Further Coding / Runtime / Production: **None**
- PHX-G523–G527: **Closed**

## Final Stop

**TRACK-G522 COMPLETE — FINAL STOP TRACK-G522.**
