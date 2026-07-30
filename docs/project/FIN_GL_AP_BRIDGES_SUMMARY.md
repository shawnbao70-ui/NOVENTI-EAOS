# Finance GL AP Bridges Summary

**Milestone:** PHX-G338  
**Alembic:** `0067_finance_gl_ap_bridges_g338`  
**Status:** TRACK-GL-AP-BRIDGES COMPLETE / TRACK-G338 COMPLETE

## Delivered

- Added nullable `ap_control` and `ap_expense` bridge-map accounts; AP bridge
  operations fail closed until both are configured.
- Added permissioned, audited, idempotent AP bill-post and AP payment-apply GL
  bridges with tenant-scoped AP read ports.
- Added gateway bridge endpoints and contract coverage while preserving GL3 AR
  bridge behavior.

## Evidence

- Coding authorization:
  `FIN_GL_AP_BRIDGES_CODING_AUTHORIZATION_SUMMARY.md`
- Boundary ADR: `ADR-0370-finance-gl-ap-bridges-boundary.md`
- Tests: `test_api_gateway_g338_finance_gl_ap_bridges.py` and GL3 regression
  contracts.
