# ADR-0076 — IdP Registry SQL Adapter (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G57  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G56 交付进程内 IdP 注册表与 Alembic `0025` 表契约，但 Gateway 未接线 SQL。需可选 SQL 适配器，默认仍为 memory。

## 决策

1. `EAOS_IDP_REGISTRY_STORE=memory|sql`（默认 `memory`）。  
2. `sql` 模式使用 `kernel.idp_issuer_bindings`（0025）+ SQLAlchemy 仓储；经 `EAOS_DATABASE_URL`（`postgresql+psycopg`）建会话；缺 URL fail-closed。  
3. API 与校验合并规则不变（env 优先）；`registry.store` 暴露 `process_memory` 或 `sql`。  
4. 同 issuer 唯一：SQL 上 disabled 行可被重新激活更新；active 冲突 → 409。  
5. 无新 Alembic；包版本仍 `0.2.0`；不双写 memory+SQL。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Discovery 写回 env  
- Service Mesh / KEDA / 多区域  
- 多区域只读副本  

## 关联

- [ADR-0075-multi-idp-write-registry.md](ADR-0075-multi-idp-write-registry.md)
- [../project/PHX-G57_ARCHITECTURE_GATE.md](../project/PHX-G57_ARCHITECTURE_GATE.md)
