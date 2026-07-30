# ADR-0151 — OIDC Login / Callback OpenAPI Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G132  
**归属：** API Contracts / Auth boundary

## 背景

G131 已交付 `auth.openapi.yaml` status 三件套。运行时 OIDC Authorization Code login/callback 与 providers 目录仍未入契约。

## 决策

1. 在既有 `auth.openapi.yaml` 增补：  
   `GET /auth/oidc/login`、`GET /auth/oidc/callback`、`GET /auth/oidc/providers`。  
2. login/callback 以 redirect（302）为主；callback 在 `Accept: application/json` 时返回 `OidcTokenEnvelope`。  
3. 路径级 `security: []`；不收录 refresh/logout/MFA enrollment（另批）。  
4. 无运行时变更；Manifest 仍 12 份；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- OIDC refresh / logout / MFA enrollment OpenAPI  
- WebAuthn 注册产品页  
- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0150-auth-openapi-status-catalog.md](ADR-0150-auth-openapi-status-catalog.md)
- [../project/PHX-G132_ARCHITECTURE_GATE.md](../project/PHX-G132_ARCHITECTURE_GATE.md)
