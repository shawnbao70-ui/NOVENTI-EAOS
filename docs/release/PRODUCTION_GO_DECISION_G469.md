# Production GO Decision — Batch M（PHX-G464–G469）· PROD1

**System-generated governance artifact**  
**Baseline:** package `0.2.5` · Alembic `0092_finance_realized_fx_gl_bridge_g372`  
**Tip stop:** FINAL STOP TRACK-G525  
**Decision:** **GO for unconditional production promotion**（evidence complete 2026-07-30）

## Evidence

| Gate | Evidence | Result |
|---|---|---|
| G464 branch protection | https://github.com/shawnbao70-ui/NOVENTI-EAOS · `main` protected；see `BRANCH_PROTECTION.md` Evidence record | **VERIFIED** |
| G465 Docker image smoke | https://github.com/shawnbao70-ui/NOVENTI-EAOS/actions/runs/30513194462/job/90777413453 · SHA `6b6457daad79e63e072e9ea426307b139b74fad8` · job `docker import smoke (optional host)` | **GREEN** |
| G466 PostgreSQL critical | Dedicated `eaos_test` on `127.0.0.1:5432` · `_PROD1_integration_critical.txt` | **GREEN** — **43 passed / 1 skipped** |
| G467 decision | All three production evidence gates satisfied | **GO** |
| G468 operator pointers | `OPERATIONS_RUNBOOK.md`, `RELEASE_CHECKLIST.md`, `BRANCH_PROTECTION.md` | **READY** |
| G469 hygiene | Tip/package and hard-hold contracts | **READY** |

## Candidate revision

| Field | Value |
|-------|-------|
| Repository | https://github.com/shawnbao70-ui/NOVENTI-EAOS |
| Visibility | public（required for Free-plan classic branch protection） |
| Candidate SHA | `6b6457daad79e63e072e9ea426307b139b74fad8`（constraints fix; docker-smoke green） |
| CI run | https://github.com/shawnbao70-ui/NOVENTI-EAOS/actions/runs/30513194462 |
| Admin / recorder | `shawnbao70-ui` via `gh` · 2026-07-30 |

## PROD1 closeout notes

- Batch M originally closed **NO-GO**（documentation-only branch protection,
  unverified docker history, blocked PG）. That historical fail-closed posture
  does not replace the fresh PROD1 evidence above.
- Constraints pin uses `psycopg==3.3.4`（no extras）for pip≥26 legality;
  binary wheels still come from pyproject `psycopg[binary]`.
- Changing this decision again requires new contrary evidence; it does not
  require opening a new feature milestone. Fresh evidence does not require a
  new feature milestone either.

## Hard holds（unchanged）

`ENABLE_*_NETWORK` / external PSP remain OFF by default; bank-file import stays
deferred; Industry host-install is not invented; Brain/Twin commercial
auto-write and WebAuthn attestation crypto verification remain closed.

## Final stop

**TRACK-PROD1 COMPLETE — production decision GO.**
