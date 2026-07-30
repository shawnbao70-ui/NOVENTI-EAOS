# PHX-G517 Acceptance — CRM Quote Lines Managed UI

> **System-generated governance artifact** under ADR-0321.

## References

- [ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md)
- [ADR-0324](../decisions/ADR-0324-crm-quote-product-boundary.md)
- [Architecture Gate](CRM_QUOTE_LINES_MANAGED_UI_ARCHITECTURE_GATE.md)
- [Coding Authorization](CRM_QUOTE_LINES_G517_CODING_AUTHORIZATION_SUMMARY.md)
- [PHX-G516 evidence](CRM_QUOTE_HEADER_UI_G516_ACCEPTANCE.md)

## Accepted Result

**PHX-G517 COMPLETE.**

- Added Quote Line list/detail/create/edit/archive Smart Terminal workflows.
- Lines load only for the selected governed Quote Header.
- UI projects active lines while the existing API preserves archived history.
- Quantity and unit price follow existing decimal contracts.
- Amount remains server-calculated and read-only.
- Permission defaults deny; server remains authoritative.
- Version conflicts never retry or overwrite; archive requires confirmation.
- Issue, Convert, approvals, and automatic pricing remain outside this slice.
- No backend, Repository, Database, Alembic, Kernel, or Runtime Manifest change.

## Evidence

- `tests/contracts/test_api_gateway_g517_crm_quote_lines_ui.py`
- G512–G516 regression contracts
- Focused cumulative result: **35 passed**
- Browser: `phx-g517-quote-lines-workspace.png`

## Approval Record

- Product Owner design: **Approve**
- Coding Authorization: **Approve**
- Date: 2026-07-29
- Milestone: **PHX-G517**

## Signature

System-generated from authoritative Product Owner decisions.

## Authorization State

- Architecture Gate: **Accepted**
- Coding Authorization: **Consumed by PHX-G517**
- Further Coding / Runtime / Production: **None**
- PHX-G518–G521: **Closed**

## Final Stop

**TRACK-G517 COMPLETE — FINAL STOP TRACK-G517.**
