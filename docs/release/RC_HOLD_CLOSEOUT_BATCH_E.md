# RC HOLD Closeout — Batch E（PHX-G416–G421）

**Baseline:** `0.2.3` / `0092`  
**PO auth:** Approve Batches E→L serial（2026-07-27）

## HOLD status

| HOLD | Closeout action | Result |
|------|-----------------|--------|
| 1. Docker image smoke | CI job `docker-smoke` in `.github/workflows/ci.yml` is the authoritative evidence path；local engineer host has **no Docker CLI**（宪章：不安装宿主机 Docker） | **CI-PATH READY**（G416–G417） |
| 2. PG `integration_critical` | Fixture reset drops **all** non-system schemas；tip → `EXPECTED_TIP`；DO header `flush` before lines；suite opt-in | **GREEN** — 43 passed / 1 skipped（G418–G419） |
| 3. Branch protection click | Documented checklist for human PO/admin；workflow jobs named for required checks | **DOCS READY**（G420）— click remains human |

## REPAIR FREEZE

After G421：`REPAIR FREEZE` **lifted for Eng feature batches F→L** under the standing PO serial auth.  
Unconditional **production** GO still requires CI `docker-smoke` green on a runner + human branch-protection enablement.

## Commands

```bash
# Local layout smoke (no Docker)
python deploy/docker/smoke_imports.py

# PG critical (dedicated eaos_test* only)
set EAOS_RUN_INTEGRATION_CRITICAL=1
python scripts/run_contract_shard.py integration_critical --pytest-arg=-m --pytest-arg=postgresql
```
