# ADR-0154 — Platform OpenAPI Catalog (Roles + IdP)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G135  
**归属：** API Contracts / Platform boundary

## 背景

G56–G91 已交付平台面 `/v1/platform/roles` 与 `/v1/platform/idp/*`（含 federation），并有 Terminal Admin 薄探针。OpenAPI Manifest 在 G131 增至 12 份（含 auth），但平台面仍无独立契约文件。

## 决策

1. 新增 `docs/api/platform.openapi.yaml`，收录声明角色目录与 IdP registry / federation。  
2. Release Manifest / adapters **12 → 13**。  
3. 脱敏：响应仅 `has_jwks_json`，永不回传 JWKS plaintext；body 禁止抬升 `tenant_id` / `platform_scope` / `roles`。  
4. Organization 租户生命周期仍归 `organization.openapi.yaml`（`/platform/tenants*`）。  
5. 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Role→grant 自动写入 / Role→Policy 绑定  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  
- `GET /permission/roles` OpenAPI（tenant 面；另批）  

## 关联

- [ADR-0150-auth-openapi-status-catalog.md](ADR-0150-auth-openapi-status-catalog.md)
- [../project/PHX-G135_ARCHITECTURE_GATE.md](../project/PHX-G135_ARCHITECTURE_GATE.md)
