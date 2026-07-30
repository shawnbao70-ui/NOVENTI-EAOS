# Branch Protection Checklist（PHX-G420 · PHX-G464 refresh）

**Status:** **UNVERIFIED** — documentation evidence only. Enabling and proving
GitHub settings is a **human PO / repo-admin click**.

## Required status checks（map to `.github/workflows/ci.yml`）

| Check job name | Purpose |
|----------------|---------|
| `contracts-pr (3.11)` / `contracts-pr (3.12)` | `pr_required` shard + Alembic head + pip check |
| `helm` | `helm lint` + `helm template` |
| `docker-smoke` | Image build + `/smoke_imports.py` |

## Human steps

1. GitHub → Settings → Branches → Branch protection rule on `main`/`master`.
2. Enable **Require status checks to pass before merging**.
3. Select the job names above once they have appeared on a PR.
4. Do **not** allow bypass without PO approval.

## Evidence record（PHX-G464）

Record all of the following before changing production status to GO:

- protected branch name
- required check names selected
- repository-admin identity and timestamp
- settings URL or screenshot/evidence reference
- candidate commit SHA

No evidence record was available during Batch M. The agent did not mutate
GitHub settings. See `PRODUCTION_GO_DECISION_G469.md`.

### PROD1 refresh（2026-07-29）

Still **UNVERIFIED**. Agent environment had no `gh` and did not change GitHub
branch settings. Fill the Evidence record fields above before any GO claim.

## Non-goals

- Agent mutation of GitHub org/host settings  
- Claiming production GO solely from docs without CI green history
