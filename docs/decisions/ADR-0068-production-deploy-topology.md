# ADR-0068 — Production Deploy Topology & Runbook (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G49  
**归属：** Platform Release / Operations boundary

## 背景

R17 交付了安装、迁移与发布门禁，但明确延后生产 FastAPI 部署拓扑。Foundation 需要一份**单主机参考拓扑**与可执行 Runbook 扩展，作为后续 Compose/K8s 的规范源，而非实现容器编排。

## 决策

1. 参考拓扑固定为：**单主机** = PostgreSQL + Gateway（uvicorn）+ Alembic migrate；Smart Terminal 由同一 Gateway 进程静态服务（`/terminal/`）。  
2. 规范文档：`docs/release/PRODUCTION_TOPOLOGY.md`；`OPERATIONS_RUNBOOK.md` 引用并补充生产启动/健康/回滚步骤。  
3. 生产默认安全基线：`EAOS_REQUIRE_JWT=1`、`EAOS_ALLOW_DEV_CONTEXT_HEADERS=0`；OIDC/JWKS/denylist/验签按业务需要 opt-in。  
4. 契约测试断言文档存在、关键章节与关键环境变量名；不引入 Docker/K8s 清单。  
5. 不 bump 包版本（仍为 `0.2.0`）；无 Alembic 变更。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Ingress / 多区域（Compose/Helm Foundation 见 ADR-0069/0070）  
- 多区域 failover / 只读副本拓扑  
- CI 托管与公有镜像仓库  
- 多 IdP 联邦管理 UI  

## 关联

- [ADR-0032-release-train-boundary.md](ADR-0032-release-train-boundary.md)
- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G49_ARCHITECTURE_GATE.md](../project/PHX-G49_ARCHITECTURE_GATE.md)
- [../release/PRODUCTION_TOPOLOGY.md](../release/PRODUCTION_TOPOLOGY.md)
