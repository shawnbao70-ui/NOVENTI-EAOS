# ADR-0020 — Identity HTTP API 契约边界

**状态：** 已接受  
**日期：** 2026-07-18  
**里程碑：** PHX-006

## 决策

1. `docs/api/identity.openapi.yaml` 是 PHX-006 Identity HTTP 契约真相源，格式为 OpenAPI 3.1。
2. API 版本通过 URI `/v1` 显式表达。
3. `subject_id`、`tenant_id`、`session_id` 与 `platform_scope` 必须由受信认证/网关层派生，不接受客户端 header 或 body 声明。
4. 客户端仅可传入 `X-Correlation-ID`；缺省时由入口层生成。
5. API 使用 Bearer security scheme 描述认证边界，但 PHX-006 不实现 OAuth/OIDC/JWT。
6. 跨租户 AI 改派只暴露协调式 reassignments 资源，不暴露绕过 Organization 收敛的领域原语。
7. OpenAPI 覆盖当前 Identity Subject、AI Profile、Credential、Session、Governor、Assignment 能力。
8. 稳定 Kernel error code 放入统一错误响应；HTTP 映射不改变 Kernel code。

## 非目标

- FastAPI/router/controller 实现
- Token 签发与校验
- OAuth/OIDC discovery
- SDK 生成与外部发布

## 关联

- [../api/identity.openapi.yaml](../api/identity.openapi.yaml)
- [../architecture/IDENTITY_INTERFACE.md](../architecture/IDENTITY_INTERFACE.md)
- [ADR-0019-identity-organization-l2.md](ADR-0019-identity-organization-l2.md)
