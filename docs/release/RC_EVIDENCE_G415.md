# Remediation Release Candidate Evidence — PHX-G415

**Date:** 2026-07-27  
**Baseline:** package `0.2.3` · Alembic `0092_finance_realized_fx_gl_bridge_g372`  
**Authority:** Targeted Remediation serial · REPAIR FREEZE

## Gate results

| Gate | Required evidence | Result |
|------|-------------------|--------|
| G0 — Repair baseline | Tip helper；no `0049`-as-current-head；G193 tip-consistent | **PASS**（G406） |
| G1 — Build integrity | Docker `noventi/` + import smoke；pip constraints；Helm/version `0.2.3` | **PARTIAL PASS** — layout/Dockerfile/Helm/constraints green；**local Docker CLI absent**（CI `docker-smoke` job is the container evidence path） |
| G2 — Governance truth | Status/ENG tip/DAL/roadmap/layout parity | **PASS**（G411） |
| G3 — Security posture | Production auth fail-closed；WebAuthn challenge-bound；network/PSP defaults OFF；K8s harden thin | **PASS**（G412–G413） |
| G4 — RC pack | Clean CI definition + `pr_required` + evidence sheet | **CONDITIONAL** — see decision |

## Evidence artifacts

| Artifact | Path |
|----------|------|
| Tip helper | `tests/contracts/_baseline.py` |
| Contract shards | `tests/contracts/shards.yaml` · `docs/release/CONTRACT_SHARDS.md` |
| CI + lock | `.github/workflows/ci.yml` · `constraints/production.txt` · `docs/release/CI_AND_LOCK.md` |
| Version parity | Helm Chart/appVersion/image.tag = `0.2.3` |
| Production auth | `api/gateway/production_auth.py` |
| K8s harden | `deploy/helm/eaos/templates/gateway-deployment.yaml` |
| PG subset | `integration_critical` shard（requires `EAOS_TEST_DATABASE_URL`） |
| Layout | `docs/project/RUNTIME_PACKAGE_LAYOUT.md` |

## Measured

| Check | Result |
|-------|--------|
| `python scripts/run_contract_shard.py pr_required` | **54.0 s** / 65 passed · 1 skipped（budget ≤600s） |
| Local Docker image smoke | **NOT RUN** — Docker CLI unavailable on engineer host；not installing host Docker without PO |
| PG critical subset | **GREEN after Batch E** — see `RC_HOLD_CLOSEOUT_BATCH_E.md`（43 passed / 1 skipped） |

## Decision

```text
REMEDIATION RC DECISION: CONDITIONAL GO
```

**GO for:** tip/package truth, contract PR feedback, version parity, CI definition, production auth code path, K8s harden thin, governance tip reconciliation.

**HOLD before unconditional production GO:**

1. CI `docker-smoke` green on a runner with Docker（or PO-authorized local Docker）  
2. `integration_critical` green against dedicated `eaos_test` database  
3. Human enablement of GitHub required status checks（branch protection click）

Feature milestones remain frozen under REPAIR FREEZE until Product Owner reopens the queue after these HOLDs.
