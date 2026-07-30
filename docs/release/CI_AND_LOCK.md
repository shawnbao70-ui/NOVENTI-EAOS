# CI and Dependency Lock（PHX-G410）

**Milestone:** PHX-G410  
**Workflow:** `.github/workflows/ci.yml`  
**Lock:** `constraints/production.txt`

## Strategy（one lock）

1. Install with constraints:  
   `pip install -e ".[persistence,api,dev]" -c constraints/production.txt`
2. `pip check` must be clean.
3. Docker / CI use the same constraints file for reproducible direct deps.
4. Bump pins only in an authorized slice; record in CHANGELOG.

## Required checks

| Job | Evidence |
|-----|----------|
| `contracts-pr` | Python 3.11/3.12 · pip check · Alembic head `0092` · `pr_required` shard · version parity |
| `helm` | `helm lint` + `helm template` |
| `docker-smoke` | image build + `/smoke_imports.py` |

## Branch protection

Enabling “required status checks” on the default branch is a **human PO / repo-admin click**.  
This slice ships the workflow only; it does not mutate host GitHub org settings.

## Non-goals

- Full matrix sprawl  
- Buying infra  
- Host Docker Desktop install on engineer laptops（CI runners provide Docker）
