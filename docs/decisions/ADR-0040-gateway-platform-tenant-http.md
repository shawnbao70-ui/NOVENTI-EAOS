# ADR-0040 — Gateway Platform Tenant Lifecycle HTTP

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G25  
**归属：** Platform API Gateway

## 背景

G21 交付 Organization 租户面 HTTP，并显式延后平台租户生命周期。OpenAPI 已定义 `/platform/tenants*`；Kernel 要求 `platform_scope=True` 与 platform governor。

## 决策

### 1. 平台上下文派生

- 新增 `derive_platform_context`：仅用于 `/v1/platform/*` 路由
- `platform_scope=True`，`tenant_id=None`
- 受信头：`X-EAOS-Subject-Id` / `X-EAOS-Subject-Type` / `X-Correlation-Id`
- **不**从 `X-EAOS-Tenant-Id` 或 body 写入上下文（忽略/拒绝覆盖）
- 租户面路由继续使用 `derive_tenant_context`（`platform_scope=False`）；客户端无法通过改 header 提升租户面路由

### 2. 本切片路由

- `POST /v1/platform/tenants`
- `POST /v1/platform/tenants/{tenantId}/suspension`
- `DELETE /v1/platform/tenants/{tenantId}/suspension`（reactivate）

### 3. Explicit Defer

JWT/OIDC 真实认证提供商；非 Organization 的其他平台面；商业 Marketplace

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [ADR-0036-gateway-organization-http-surface.md](ADR-0036-gateway-organization-http-surface.md)
- [../project/PHX-G25_ARCHITECTURE_GATE.md](../project/PHX-G25_ARCHITECTURE_GATE.md)
