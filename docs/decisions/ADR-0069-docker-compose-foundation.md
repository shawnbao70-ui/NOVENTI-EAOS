# ADR-0069 — Docker Compose Foundation (Single-Host)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G50  
**归属：** Platform Release / Operations boundary

## 背景

G49 规范了单主机 Gateway + PostgreSQL 拓扑，但未交付可运行的编排清单。Foundation 需要一份最小 Compose 参考实现，映射该拓扑，而非 Kubernetes 产品化。

## 决策

1. 交付路径：`deploy/docker/`（`Dockerfile`、`compose.yaml`、`entrypoint.py`、`.env.example`）。  
2. 服务：`db`（PostgreSQL）+ `gateway`（migrate → uvicorn）；Gateway 依赖 DB healthcheck。  
3. 镜像构建上下文为仓库根；安装 `.[persistence,api]` + `PyYAML`（release manifest）。  
4. 生产安全基线与 G49 一致（`REQUIRE_JWT=1`、关闭开发头）；密钥仅经 env / `.env`（不入库）。  
5. 契约断言 Compose 文件存在、可解析、含 `db`/`gateway` 与关键 env；不在 CI 强制 `docker build`。  
6. 不 bump 包版本（仍 `0.2.0`）；无 Alembic 变更；不交付 Helm/K8s。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Kubernetes / Helm Foundation（见 ADR-0070 / PHX-G51）；公有镜像仓库推送仍延后  
- 多区域 / 多副本编排  
- 多 IdP 联邦管理 UI  
- 托管 CI 推送镜像  

## 关联

- [ADR-0068-production-deploy-topology.md](ADR-0068-production-deploy-topology.md)
- [ADR-0070-helm-foundation.md](ADR-0070-helm-foundation.md)
- [../project/PHX-G50_ARCHITECTURE_GATE.md](../project/PHX-G50_ARCHITECTURE_GATE.md)
- [../release/COMPOSE.md](../release/COMPOSE.md)
