# Finance Realized FX → GL Bridge G372 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G372  
**Authorization:** `FIN_REALIZED_FX_GL_BRIDGE_CODING_AUTHORIZATION_SUMMARY.md`  
**ADR:** [ADR-0400](../decisions/ADR-0400-finance-realized-fx-gl-bridge-boundary.md)

- Added Alembic revision `0092_finance_realized_fx_gl_bridge_g372` revising
  `0091_finance_treasury_transfer_g371`, extending
  `ck_gl_bridge_postings_source_type_valid` with `realized_fx`.
- `GlBridgeSourceType.REALIZED_FX`; `FinanceService.bridge_realized_fx`
  requires open period, map `fx_gain`/`fx_loss`, positive amount, and
  idempotent `source_type`+`source_id` (+ key). Journal convention:
  gain Dr `ar_control` / Cr `fx_gain`; loss Dr `fx_loss` / Cr `ar_control`.
  No auto-bridge on allocation (ADR-0400).
- HTTP: `POST /v1/finance/gl-bridges/realized-fx`. Contracts in
  `tests/contracts/test_api_gateway_g372_realized_fx_gl_bridge.py`.

**TRACK-REALIZED-FX-GL-BRIDGE COMPLETE / TRACK-G372 COMPLETE**

Tip verified: `0092_finance_realized_fx_gl_bridge_g372`  
Next: PHX-G373 (Release train readiness) queued.
