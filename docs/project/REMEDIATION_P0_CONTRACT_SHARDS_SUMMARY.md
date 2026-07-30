# PHX-G408 — Remediation P0-2 Contract Shards Summary

**Status:** TRACK-REMEDIATION-CONTRACT-SHARDS COMPLETE / TRACK-G408 COMPLETE  
**Milestone:** PHX-G408  
**Authorization:** `REMEDIATION_P0_CONTRACT_SHARDS_CODING_AUTHORIZATION_SUMMARY.md`

- Added `tests/contracts/shards.yaml` with domain shards + `pr_required`.
- Runner `scripts/run_contract_shard.py` prints `DURATION_SECONDS` and fails
  `pr_required` if wall-clock exceeds 600 s.
- Docs：`docs/release/CONTRACT_SHARDS.md`（ownership + duration honesty）.
- Reference measurement：`pr_required` = **53.5 s** / 47 passed（≤ 10 min）.
- Full `tests/contracts` remains nightly/parallel — latency must be published, not hidden.
- No flaky skips；no Alembic；package remains `0.2.3`.

Tip verified: `0092_finance_realized_fx_gl_bridge_g372`  
Package verified: `0.2.3`  
Next: PHX-G409（await separate Coding Auth）— P1-3 Helm/version parity → 0.2.3.
