# ADR-0035 — Gateway Identity HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G20  
**归属：** Platform API Gateway

## 背景

PHX-G18 交付最小网关与受信上下文派生；PHX-R17 契约目录仍为真相源。下一步需证明「HTTP → Kernel」薄适配，而不将业务规则迁入网关。

## 决策

### 1. 试点域

Identity 垂直切片（subject / credential / session），路径对齐 `docs/api/identity.openapi.yaml`：

- `POST /v1/identity/subjects`
- `GET /v1/identity/subjects/{subjectId}`
- `POST /v1/identity/credentials`
- `POST /v1/identity/sessions`
- `GET /v1/identity/sessions/{sessionId}/validation`

### 2. 适配边界

- Router 仅做：受信头上下文、请求解析、调用 Identity 服务、`KernelResult` → HTTP
- 服务通过 `app.state.identity` / `create_app(identity_service=...)` 注入；默认 `IdentityService()`（内存）
- 请求体中的资源 `subject_id`（绑定凭证）允许；`tenant_id` / `platform_scope` 仍禁止覆盖上下文
- OpenAPI `ttl_minutes` → 服务 `ttl_seconds`（×60）

### 3. Explicit Defer

- AI Employee / Governor / revoke* HTTP
- JWT/OIDC；其他域全量路由
- Marketplace 商业 API

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G20_ARCHITECTURE_GATE.md](../project/PHX-G20_ARCHITECTURE_GATE.md)
