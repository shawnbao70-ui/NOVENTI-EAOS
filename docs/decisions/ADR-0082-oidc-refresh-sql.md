# ADR-0082 — OIDC Refresh Binding SQL Adapter

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G63  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G61 将 IdP `refresh_token` / `id_token` 绑定在进程内存。需可选 SQL 持久化，默认仍为 memory。

## 决策

1. `EAOS_OIDC_REFRESH_STORE=memory|sql`（默认 `memory`）。  
2. `sql` 使用 `kernel.oidc_refresh_bindings`（Alembic `0026`）+ SQLAlchemy 仓储；经 `EAOS_DATABASE_URL`（`postgresql+psycopg`）；缺 URL fail-closed。  
3. API 行为不变；`/v1/auth/oidc/status` 暴露 `refresh_store`（`process_memory`|`sql`）。  
4. 令牌明文落库（与现有密钥运维边界一致）；不在 status/API 响应回传 refresh/id_token。  
5. 包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 令牌字段应用层加密  
- 组织级联邦 UI / 网格 CRD / 多区域  

## 关联

- [ADR-0080-oidc-refresh-rp-logout.md](ADR-0080-oidc-refresh-rp-logout.md)
- [../project/PHX-G63_ARCHITECTURE_GATE.md](../project/PHX-G63_ARCHITECTURE_GATE.md)
