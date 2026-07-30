# ADR-0104 — OIDC Per-Provider Refresh Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G85  
**归属：** Platform API Gateway / OIDC

## 背景

G84 多 provider 登录后，refresh/logout 仍一律走主 `EAOS_OIDC_*` token/client，社交 IdP 换码会失败。

## 决策

1. 登录 callback 若带 `provider_key`，在 EAOS JWT 写入 `eaos_oidc_login_provider`。  
2. `POST /refresh` / `POST /logout` 读取该 claim，经 `resolve_login_oidc_settings` 选择 client/token（及 logout 的 `client_id`）。  
3. 主登录无该 claim → 行为与 G61 完全一致。  
4. claim 指向已移除的 provider → `400` + `GATEWAY_OIDC_UNKNOWN_PROVIDER`（fail-closed）。  
5. 无 Alembic；不扩展 refresh SQL schema；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Provider 级独立 `end_session_endpoint` 目录字段（见 ADR-0105 / PHX-G86）  
- MFA 注册 / WebAuthn UX  
- Role 目录 / 自动写 grant  

## 关联

- [ADR-0103-oidc-multi-provider-login.md](ADR-0103-oidc-multi-provider-login.md)
- [ADR-0080-oidc-refresh-rp-logout.md](ADR-0080-oidc-refresh-rp-logout.md)
- [../project/PHX-G85_ARCHITECTURE_GATE.md](../project/PHX-G85_ARCHITECTURE_GATE.md)
