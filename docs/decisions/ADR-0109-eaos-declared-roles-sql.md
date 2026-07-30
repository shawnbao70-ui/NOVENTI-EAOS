# ADR-0109 — Declared EAOS Roles Catalog SQL Store

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G90  
**归属：** Platform API Gateway / Permission

## 背景

G88 只读聚合 env/OIDC/grant map。声明角色需可持久化管理，但不自动写 grants。

## 决策

1. `EAOS_ROLE_CATALOG_STORE=memory|sql`（默认 `memory`）；`sql` 需 `EAOS_DATABASE_URL`。  
2. 表 `kernel.eaos_declared_roles`（name/status/version/timestamps）；Alembic `0029_eaos_declared_roles_g90`。  
3. 平台面：`GET/POST /v1/platform/roles`、`POST .../{id}/disable`。  
4. 租户 `GET /v1/permission/roles`：env ∪ **active** store 作为 `catalog` 源；永不写 grants。  
5. 包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0107-eaos-roles-catalog.md](ADR-0107-eaos-roles-catalog.md)
- [../project/PHX-G90_ARCHITECTURE_GATE.md](../project/PHX-G90_ARCHITECTURE_GATE.md)
