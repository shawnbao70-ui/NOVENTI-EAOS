# ADR-0105 — OIDC Provider End-Session Catalog Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G86  
**归属：** Platform API Gateway / OIDC

## 背景

G85 logout 已用 provider `client_id`，但 `end_session_endpoint` 仍恒取自主配置，社交 IdP RP-Logout 可能指错主机。

## 决策

1. `EAOS_OIDC_LOGIN_PROVIDERS` 可选第 7 段：`end_session`（允许空 authorize/token 占位）。  
2. `resolve_login_oidc_settings`：provider 有 `end_session_endpoint` 则用之，否则回落主配置。  
3. `/providers` 与 status 暴露 `has_end_session`；有值时附带 `end_session_endpoint`（非密钥）。  
4. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  
- Provider Discovery 自动填 end_session  

## 关联

- [ADR-0103-oidc-multi-provider-login.md](ADR-0103-oidc-multi-provider-login.md)
- [ADR-0104-oidc-provider-refresh.md](ADR-0104-oidc-provider-refresh.md)
- [../project/PHX-G86_ARCHITECTURE_GATE.md](../project/PHX-G86_ARCHITECTURE_GATE.md)
