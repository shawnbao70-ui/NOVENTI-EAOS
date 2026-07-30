# ADR-0153 — OIDC MFA Enrollment OpenAPI Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G134  
**归属：** API Contracts / Auth boundary

## 背景

G89 已交付 `GET /v1/auth/oidc/mfa-enrollment`（配置 URL → 302 重定向）。G131–G133 将 Auth OpenAPI 补齐至 refresh/logout，但仍未收录该出口。本切片**不是** WebAuthn / MFA 注册产品页。

## 决策

1. 在既有 `auth.openapi.yaml` 增补 `GET /auth/oidc/mfa-enrollment`（public；302 / 503）。  
2. 明确文档：依赖 `EAOS_OIDC_MFA_ENROLLMENT_URL`；≠ WebAuthn 产品面。  
3. 无运行时变更；Manifest 仍 12 份；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0152-oidc-refresh-logout-openapi.md](ADR-0152-oidc-refresh-logout-openapi.md)
- [../project/PHX-G134_ARCHITECTURE_GATE.md](../project/PHX-G134_ARCHITECTURE_GATE.md)
