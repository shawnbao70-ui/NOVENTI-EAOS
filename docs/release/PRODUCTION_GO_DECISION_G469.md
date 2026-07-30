# Production GO Decision — Batch M（PHX-G464–G469）

**System-generated governance artifact**  
**Baseline:** package `0.2.5` · Alembic `0092_finance_realized_fx_gl_bridge_g372`  
**Tip stop:** FINAL STOP TRACK-G525  
**Decision:** **NO-GO for unconditional production promotion**

## Evidence

| Gate | Evidence | Result |
|---|---|---|
| G464 branch protection | Human procedure documented in `BRANCH_PROTECTION.md`; `gh` logged in as `shawnbao70-ui` | **UNVERIFIED** — no GitHub repository visible under this account; no admin evidence record |
| G465 Docker image smoke | `.github/workflows/ci.yml` defines `docker-smoke` | **UNVERIFIED HISTORY** — no CI runs / green job URL (no bound remote repo under `shawnbao70-ui`) |
| G466 PostgreSQL critical | Dedicated `eaos_test` on `127.0.0.1:5432` | **GREEN** — `integration_critical` **43 passed / 1 skipped**（2026-07-29；`_PROD1_integration_critical.txt`） |
| G467 decision | Fail closed when any required production gate lacks evidence | **NO-GO** |
| G468 operator pointers | `OPERATIONS_RUNBOOK.md`, `RELEASE_CHECKLIST.md`, `BRANCH_PROTECTION.md` | **READY** |
| G469 hygiene | Tip/package and hard-hold contracts | **READY** |

## PROD1 attempt（2026-07-29 → 2026-07-30）

Wave **PRODUCTION_GO / PROD1** executed under PO sequencing choice **A**.

- No new PHX-G feature invent; no Alembic; hard holds unchanged.
- GitHub CLI installed; authenticated as **`shawnbao70-ui`** (scopes include
  `repo`, `workflow`).
- Local workspace has **no `.git` remote**; account **`shawnbao70-ui` lists zero
  repositories** — cannot bind branch-protection or CI to a candidate SHA yet.
- Branch-protection: still **UNVERIFIED** (no target repo / admin evidence).
- docker-smoke: still **UNVERIFIED HISTORY** (no workflow runs under this account).
- integration_critical: **GREEN** on dedicated `eaos_test` at `127.0.0.1:5432`
  — **43 passed / 1 skipped**（2026-07-29；log
  `docs/release/_PROD1_integration_critical.txt`）.
- Decision remains **NO-GO** (fail-closed). GO was not invented.

## Decision rationale

This decision refreshes Batch M / PROD1 evidence status without claiming that
production is ready. A workflow definition is not CI history, documentation is
not a branch-protection setting, and a configured DSN is not a green suite run.

## Conditions to change NO-GO to GO

1. A repository admin enables required checks and records the protected branch
   and selected checks in `BRANCH_PROTECTION.md` Evidence record.
2. A CI runner records a green `docker-smoke` job for the candidate revision
   (URL + SHA).
3. `integration_critical` completes green against a dedicated `eaos_test*`
   PostgreSQL database (reachable DSN; suite output retained).
4. The release owner records the candidate SHA and evidence URLs in this file.

Changing this decision requires new evidence; it does not require opening a
new feature milestone.

## Hard holds

`ENABLE_*_NETWORK` / external PSP remain OFF by default; bank-file import stays
deferred; Industry host-install is not invented; Brain/Twin commercial
auto-write and WebAuthn attestation crypto verification remain closed.

## Final stop

**TRACK-PROD1 COMPLETE — STOP.** Production decision remains **NO-GO**.
