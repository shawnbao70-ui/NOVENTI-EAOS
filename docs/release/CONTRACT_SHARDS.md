# Contract Suite Shards（PHX-G408）

**Milestone:** PHX-G408  
**Manifest:** `tests/contracts/shards.yaml`  
**Runner:** `python scripts/run_contract_shard.py <shard>`  
**Package / tip:** Foundation `0.2.4` / Alembic `0092`（not redefined here）

## Purpose

Make contract feedback usable on every PR without hiding full-suite latency.

| Track | Shard | Ownership | Budget / schedule |
|-------|-------|-----------|-------------------|
| Required PR | `pr_required` | Platform + Test | **≤ 600 s（10 min）** · every PR |
| Parallel / nightly | `baseline` | Release | nightly_or_parallel |
| Parallel / nightly | `ops_release` | Platform | nightly_or_parallel |
| Parallel / nightly | `docs` | Architecture + Release | nightly_or_parallel |
| Parallel / nightly | `openapi_auth` | Identity / Auth | nightly_or_parallel |
| Parallel / nightly | `openapi_terminal` | Terminal | nightly_or_parallel |
| Parallel / nightly | `openapi_remainder` | Platform | nightly_or_parallel |
| Parallel / nightly | `domain_runtime` | Domain | nightly_or_parallel |
| Full suite | `full_contracts` | Platform + Test | **nightly** — publish duration |

## How to run

```bash
# Required PR set (must stay ≤10 minutes on reference workstation)
python scripts/run_contract_shard.py pr_required

# Example parallel shard
python scripts/run_contract_shard.py baseline

# Full contracts (expect long wall-clock; publish DURATION_SECONDS)
python scripts/run_contract_shard.py full_contracts
```

Runner prints `DURATION_SECONDS=` and exits `2` if `pr_required` exceeds budget even when tests pass.

## Duration honesty

- **Do not hide** full-suite latency behind a green required PR set.
- Publish `DURATION_SECONDS` from the runner (CI logs or release evidence).
- Expanding `pr_required` requires measuring wall-clock and keeping ≤ 600 s, or moving coverage into a nightly shard.

## Reference measurement（PHX-G408 cut）

Recorded 2026-07-27 on a single-engineer Windows workstation（Python 3.12）:

| Shard | DURATION_SECONDS | Result |
|-------|------------------|--------|
| `pr_required` | **109.0**（G511 cut；was 63.3 at G469） | 119 passed · 1 skipped · within 600 s budget |
| `full_contracts` | *(publish when run)* | nightly / parallel — not a PR gate |

**Do not hide** full-suite latency: when `full_contracts` is run, record and publish its `DURATION_SECONDS` beside the required PR result.

## Non-goals

- Inventing flaky skips to meet budget  
- Claiming full OpenAPI softener coverage inside `pr_required`  
- Host CI platform install（GitHub Actions land under later PHX-G410）

## Integration critical（Batch F publish）

| Suite | Opt-in | Reference result（Batch E/F） |
|-------|--------|------------------------------|
| `integration_critical` | `EAOS_RUN_INTEGRATION_CRITICAL=1` + `EAOS_TEST_DATABASE_URL` on dedicated `eaos_test*` | **43 passed / 1 skipped** · ~60 s（2026-07-27） |

Forward-only upgrade + schema reset is the supported path；mid-chain downgrade remains deferred.
