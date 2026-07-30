# ADR-0037 — Gateway Permission HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G22  
**归属：** Platform API Gateway

## 背景

G20/G21 已交付 Identity / Organization 租户面薄适配。Permission OpenAPI 与 Kernel 服务已成熟，可在同一受信边界下接线。

## 决策

### 1. 本切片路由

对齐 `docs/api/permission.openapi.yaml`：

- `POST /v1/permission/policies`
- `POST /v1/permission/policies/{policyId}/activation`
- `POST /v1/permission/grants`
- `POST /v1/permission/grants/{grantId}/revocation`
- `POST /v1/permission/evaluations`（principal = 受信头 subject）
- `GET /v1/permission/decisions/{decisionId}/explanation`
- `GET /v1/permission/principals/{subjectId}/effective-permissions`

### 2. 适配规则

- `app.state.permission` 注入；默认 `PermissionService()`
- Body 禁止 `tenant_id` / `platform_scope`
- OpenAPI `principal_id` / `scope_ref_id` 为资源字段，映射到服务参数
- `CreatePolicyRequest` 无 `policy_version` 时默认 `"1"`
- Evaluate 不以 body 指定 principal（防冒充）

### 3. Explicit Defer

deprecate / delegate HTTP；OIDC；平台面

## 关联

- [ADR-0035-gateway-identity-http-surface.md](ADR-0035-gateway-identity-http-surface.md)
- [../project/PHX-G22_ARCHITECTURE_GATE.md](../project/PHX-G22_ARCHITECTURE_GATE.md)
