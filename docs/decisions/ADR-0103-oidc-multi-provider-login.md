# ADR-0103 — OIDC Multi-Provider Login Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G84  
**归属：** Platform API Gateway / OIDC

## 背景

OIDC 登录仅绑定单一 `EAOS_OIDC_*`。社交/多 IdP 登录需要可选第二方 authorize，但不做完整社交产品页或 MFA 注册。

## 决策

1. 可选 env `EAOS_OIDC_LOGIN_PROVIDERS`：`key|issuer|client_id|client_secret[:|authorize|token],...`；空=关闭。  
2. `GET /v1/auth/oidc/login?provider=<key>` 用目录项覆盖 issuer/client/authorize/token；`redirect_uri` / scopes / default tenant 继承主配置。  
3. 登录 state 记录 `provider_key`；callback 用同一 overlay 换码。  
4. `GET /v1/auth/oidc/providers` 与 status 暴露脱敏目录（key/issuer only）。  
5. 未知 provider → `400` + `GATEWAY_OIDC_UNKNOWN_PROVIDER`。  
6. Terminal 薄渲染额外登录链接；无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 按 provider 的 refresh/logout token endpoint 路由（见 ADR-0104 / PHX-G85）  
- MFA 注册 / WebAuthn UX  
- 完整社交品牌按钮与账号关联产品流  

## 关联

- [ADR-0058-oidc-authorization-code-login.md](ADR-0058-oidc-authorization-code-login.md)
- [../project/PHX-G84_ARCHITECTURE_GATE.md](../project/PHX-G84_ARCHITECTURE_GATE.md)
