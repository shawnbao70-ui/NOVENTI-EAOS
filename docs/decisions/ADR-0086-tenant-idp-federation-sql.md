# ADR-0086 — Tenant IdP Federation Binding SQL Adapter

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G67  
**归属：** Platform API Gateway / Persistence boundary

## 背景

G66 交付进程内租户↔issuer 绑定。需可选 SQL 持久化，默认仍为 memory。

## 决策

1. `EAOS_TENANT_IDP_FEDERATION_STORE=memory|sql`（默认 `memory`）。  
2. `sql` 使用 `kernel.tenant_idp_bindings`（Alembic `0027`）+ SQLAlchemy 仓储；经 `EAOS_DATABASE_URL`（`postgresql+psycopg`）；缺 URL fail-closed。  
3. API 行为不变；`federation.store` 为 `process_memory`|`sql`（不可用时 `unavailable`）。  
4. `(tenant_id, lower(issuer))` 唯一；disable 软禁用；同键可 reactivate。  
5. 包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 联邦 UI / JWT 强制绑定 / social login  
- 网格 CRD / 多区域 / KMS  

## 关联

- [ADR-0085-tenant-idp-federation-binding.md](ADR-0085-tenant-idp-federation-binding.md)
- [../project/PHX-G67_ARCHITECTURE_GATE.md](../project/PHX-G67_ARCHITECTURE_GATE.md)
