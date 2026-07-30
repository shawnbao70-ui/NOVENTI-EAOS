# Inventory DO Ship Ledger Architecture Gate

**状态：** Gate Accepted（design boundary only）  
**规范源：** ADR-0338  
**证据：** `INV_DO_SHIP_AUTHORIZATION_SUMMARY.md` (PO Approve 2026-07-25)

## Invariants

1. Package ownership: `noventi.inventory`; not Kernel / not external WMS.
2. Ship requires released DO, confirmed SO, clear commercial hold, human_confirm.
3. One ship posting per DO; idempotent by ship key; stock fail-closed.
4. Ledger row `do_ship` and on_hand decrement are atomic with the posting.
5. CRM DO status mirrors to `shipped`; Inventory does not call CRMService.
6. Permission default-deny; audit details empty.

## Decision

Accepted through Product Owner conversation authorization (Wave I / I1).
