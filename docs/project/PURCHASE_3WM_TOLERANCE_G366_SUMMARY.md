# Purchase Three-Way Match Tolerance G366 Summary

**Status:** System-generated governance artifact — COMPLETE  
**Milestone:** PHX-G366  
**Authorization:** `PURCHASE_3WM_TOLERANCE_CODING_AUTHORIZATION_SUMMARY.md`

- Added Alembic revision `0088_purchase_3wm_tolerance_g366`.
- Added tenant-scoped amount tolerance policy
  (`amount_tolerance_abs`, `amount_tolerance_pct`; default zero = exact)
  with protected GET/PUT at
  `/v1/purchase/policies/three-way-match-tolerance`.
- `create_three_way_match` applies the greater of absolute and percent
  allowances when comparing PO expected total vs AP bill total; outside
  tolerance remains mismatch (never silent matched).
- Contract coverage verifies default exact match, within-tolerance match,
  outside-tolerance mismatch, percent path, and closed OpenAPI.

**TRACK-3WM-TOLERANCE COMPLETE / TRACK-G366 COMPLETE**
