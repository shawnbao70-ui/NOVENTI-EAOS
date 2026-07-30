# ADR-0152 — OIDC Refresh / Logout OpenAPI Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G133  
**归属：** API Contracts / Auth boundary

## 背景

G131–G132 已将 Auth status 与 OIDC login/callback/providers 纳入 `auth.openapi.yaml`。运行时 `POST /auth/oidc/refresh` 与 `POST /auth/oidc/logout`（G61）仍未入契约。

## 决策

1. 在既有 `auth.openapi.yaml` 增补 Bearer-gated refresh / logout。  
2. refresh 复用 `OidcTokenEnvelope`；logout 用 `OidcLogoutEnvelope`（可含 caller `jti` 与可选 `end_session_url`；不下发 IdP refresh_token）。  
3. MFA enrollment OpenAPI 另批。  
4. 无运行时变更；Manifest 仍 12 份；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- OIDC MFA enrollment OpenAPI  
- WebAuthn 注册产品页  
- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0151-oidc-login-callback-openapi.md](ADR-0151-oidc-login-callback-openapi.md)
- [../project/PHX-G133_ARCHITECTURE_GATE.md](../project/PHX-G133_ARCHITECTURE_GATE.md)
