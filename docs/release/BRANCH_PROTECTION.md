# Branch Protection Checklist（PHX-G420 · PHX-G464 refresh）

**Status:** **VERIFIED**（PROD1 · 2026-07-30）— classic branch protection enabled on
`main` via GitHub API after repository made **public**（Free plan cannot protect
private repos）. Batch M closeout historically recorded **UNVERIFIED**
documentation-only evidence; that record does not supersede PROD1 verification.

## Required status checks（map to `.github/workflows/ci.yml`）

| Check job name（actual Actions name） | Purpose |
|--------------------------------------|---------|
| `pr_required (3.11)` / `pr_required (3.12)` | `pr_required` shard + Alembic head + pip check |
| `helm lint/template` | `helm lint` + `helm template` |
| `docker import smoke (optional host)` | Image build + `/smoke_imports.py` |

## Human steps

1. GitHub → Settings → Branches → Branch protection rule on `main`/`master`.
2. Enable **Require status checks to pass before merging**.
3. Select the job names above once they have appeared on a PR.
4. Do **not** allow bypass without PO approval.

## Evidence record（PHX-G464 · PROD1）

| Field | Value |
|-------|-------|
| Repository | https://github.com/shawnbao70-ui/NOVENTI-EAOS |
| Visibility | **public**（changed 2026-07-30 for Free-plan protection） |
| Protected branch | `main` |
| Required checks | `pr_required (3.11)`, `pr_required (3.12)`, `helm lint/template`, `docker import smoke (optional host)` |
| Strict / up-to-date | **true** |
| Enforce admins | **true** |
| Allow force pushes | **false** |
| Repository-admin identity | `shawnbao70-ui`（via `gh` API） |
| Timestamp (UTC) | 2026-07-30 |
| Settings API | `GET /repos/shawnbao70-ui/NOVENTI-EAOS/branches/main/protection` |
| Candidate SHA（full eaos-ci green） | `e90dab673e3fdf48f1d25c7a89ab862948be1b0f` |

Payload retained: `docs/release/_PROD1_branch_protection_payload.json`.

See `PRODUCTION_GO_DECISION_G469.md`.

## Non-goals

- Claiming production GO solely from docs without CI green history
- Silent bypass of required checks
