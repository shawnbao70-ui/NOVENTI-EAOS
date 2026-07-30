# EAOS Docker Compose — Phoenix Foundation

**Version:** 0.2.1  
**Milestone:** PHX-G50  
**Prior Foundation baseline:** `0.2.0`（PHX-R17）  
**Normative:** ADR-0069  
**Topology:** [PRODUCTION_TOPOLOGY.md](PRODUCTION_TOPOLOGY.md) (PHX-G49)

## 1. What this maps

| Compose service | Topology role |
|-----------------|---------------|
| `db` | PostgreSQL |
| `gateway` | uvicorn Gateway + `/terminal/`；启动时 `alembic upgrade head` |

## 2. Quick start

```bash
cd H:\Workspace\NOVENTI-EAOS
copy deploy\docker\.env.example deploy\docker\.env
# edit deploy\docker\.env — set POSTGRES_PASSWORD and EAOS_JWT_SECRET
docker compose -f deploy/docker/compose.yaml --env-file deploy/docker/.env up --build
```

Smoke:

- `GET http://127.0.0.1:8000/v1/health`
- `GET http://127.0.0.1:8000/v1/release` → version `0.2.1`
- `GET http://127.0.0.1:8000/terminal/`

Stop: `docker compose -f deploy/docker/compose.yaml --env-file deploy/docker/.env down`

## 3. Artifacts

| Path | Purpose |
|------|---------|
| `deploy/docker/compose.yaml` | Services + volumes |
| `deploy/docker/Dockerfile` | Gateway image |
| `deploy/docker/entrypoint.py` | Wait DB → migrate → uvicorn |
| `deploy/docker/.env.example` | Required secrets template |

## 4. Security notes

- Never commit `deploy/docker/.env`.  
- Defaults match G49 production baseline (`EAOS_REQUIRE_JWT=1`, dev headers off).  
- Example passwords are placeholders only.  
- Marketplace payment clearing is env-gated（PHX-G162；default OFF）；external PSP / arbitration remain fail-closed.

## 5. Deploy Region (PHX-G76)

可选 `EAOS_DEPLOY_REGION`（见 `.env.example` 与 [REGION.md](REGION.md)）。空 = 未标注。

## 6. Runtime package packaging（PHX-G407）

Gateway image **must** include `noventi/`（CRM / Finance / Purchase / Inventory runtime）.

| Check | How |
|-------|-----|
| Dockerfile | `COPY noventi ./noventi` |
| Layout smoke（no Docker required） | `python deploy/docker/smoke_imports.py` with `PYTHONPATH=<repo>:<repo>/sdk` |
| Image smoke（when Docker available） | `docker build -f deploy/docker/Dockerfile -t eaos:local .` then `docker run --rm --entrypoint python eaos:local /smoke_imports.py` |

**Boundary:** this is **image packaging only**. It is **≠** host OS software install, **≠** Marketplace host-acquire runtime invent, **≠** Industry package host-install runtime.

## 7. Explicit non-goals

- Kubernetes / Helm 产品化（Foundation chart 见 [HELM.md](HELM.md) / PHX-G51）  
- 公有镜像仓库推送  
- Multi-region production SaaS / failover / multi-replica（区域标签见 G76）  
- Multi IdP admin UI  
- Package version bump beyond published Foundation baseline（see RELEASE_MANIFEST；do not treat this doc header alone as tip）  
- Installing Docker Desktop / host daemon without separate PO auth
