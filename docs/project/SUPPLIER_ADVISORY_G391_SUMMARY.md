# Supplier Advisory (Supplier360) G391 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G391  
**ADR:** [ADR-0414](../decisions/ADR-0414-supplier-advisory-supplier360.md)

- No Alembic; tip remains `0092_finance_realized_fx_gl_bridge_g372`.
- `GET .../suppliers/{id}/advisory` wraps Supplier360 with
  `execution_authority=none`.
- Contracts: `tests/contracts/test_api_gateway_g391_supplier_advisory.py`.

**TRACK-SUPPLIER-ADVISORY COMPLETE / TRACK-G391 COMPLETE**
