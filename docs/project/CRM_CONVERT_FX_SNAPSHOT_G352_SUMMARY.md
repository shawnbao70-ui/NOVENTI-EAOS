# Convert FX Snapshot G352 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G352  
**Authorization:** `CRM_CONVERT_FX_SNAPSHOT_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0076_crm_convert_fx_snapshot_g352`.
- Quote conversion snapshots transaction currency, functional currency, FX rate, and
  functional total on both QuoteConversion and SalesOrder.
- Same-currency conversion is fixed to FX rate `1`; cross-currency conversion
  fails closed without a positive rate.
- Added HTTP contract coverage for cross-currency snapshots and missing-rate rejection.

**TRACK-CONVERT-FX-SNAPSHOT COMPLETE**
