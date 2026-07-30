# ADR-0036 — Gateway Organization HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G21  
**归属：** Platform API Gateway

## 背景

PHX-G20 已证明 Identity HTTP 薄适配。Organization OpenAPI 已存在；租户面命令可经受信头上下文到达 Kernel，无需在本切片开放平台面。

## 决策

### 1. 本切片路由（租户面）

对齐 `docs/api/organization.openapi.yaml`（无 `/organization` 前缀）：

- `GET /v1/tenants/{tenantId}`
- `POST|GET /v1/enterprises`
- `PUT /v1/organization-units`
- `POST|GET /v1/memberships`

### 2. 平台面延后

- `POST /v1/platform/tenants*` 与 suspension 需 `platform_scope` + governor
- 本切片**不**新增 `derive_platform_context`；测试通过 Kernel 平台上下文种子租户

### 3. 适配边界

- Router 仅传输适配；`app.state.organization` 注入服务
- Body 禁止 `tenant_id` / `platform_scope`；资源 id（如 membership `subject_id`）允许

## Explicit Defer

平台租户生命周期 HTTP、membership 转移/结束、unit tree/status、OIDC、商业 Marketplace

## 关联

- [ADR-0035-gateway-identity-http-surface.md](ADR-0035-gateway-identity-http-surface.md)
- [../project/PHX-G21_ARCHITECTURE_GATE.md](../project/PHX-G21_ARCHITECTURE_GATE.md)
