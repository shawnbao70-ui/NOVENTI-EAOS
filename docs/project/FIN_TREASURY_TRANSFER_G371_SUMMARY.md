# Finance Treasury Transfer G371 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G371  
**Authorization:** `FIN_TREASURY_TRANSFER_CODING_AUTHORIZATION_SUMMARY.md`  
**ADR:** [ADR-0399](../decisions/ADR-0399-finance-treasury-transfer-boundary.md)

- Added Alembic revision `0091_finance_treasury_transfer_g371` revising
  `0090_inventory_controlled_reship_g370`, creating tenant-scoped
  `finance.treasury_transfers` with from/to account refs, amount, currency,
  FX fields (`functional_currency`, `fx_rate`, `functional_amount`),
  idempotency, and `draft|posted` lifecycle.
- `FinanceService.create_treasury_transfer` / `post_treasury_transfer` reuse
  `_cash_event_fx` (same fail-closed cross-currency rules as G350 cash events);
  post requires explicit `human_confirm`. No bank file import or PSP.
- HTTP: `POST` / `GET /v1/finance/treasury-transfers[/{id}]` and
  `POST .../{id}/post`. Contracts in
  `tests/contracts/test_api_gateway_g371_treasury_transfer.py`.

**TRACK-TREASURY-TRANSFER COMPLETE / TRACK-G371 COMPLETE**

Tip verified: `0091_finance_treasury_transfer_g371`  
Next: PHX-G372 (Realized FX → GL bridge) queued.
