# ADR-0066 — OIDC IdP Discovery (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G47  
**归属：** Platform API Gateway / Identity boundary

## 背景

G40 以 issuer 启发式拼接 `/authorize`、`/token`，或要求显式端点。标准 IdP 提供 OpenID Provider Metadata；需可选 Discovery 以免硬编码路径。支付清算另批。

## 决策

1. `EAOS_OIDC_DISCOVERY=1` 启用 Discovery；URL 默认 `{issuer}/.well-known/openid-configuration`，可被 `EAOS_OIDC_DISCOVERY_URL` 覆盖。  
2. 显式 `EAOS_OIDC_AUTHORIZATION_ENDPOINT` / `TOKEN_ENDPOINT` 优先于 Discovery 结果。  
3. Discovery 文档 `issuer` 必须与配置 `EAOS_OIDC_ISSUER` 一致（fail-closed）。  
4. 仅接受 HTTPS Discovery URL（loopback http 仅测试注入）。  
5. 短 TTL 进程内缓存；`/v1/auth/oidc/status` 暴露 `discovery` 与解析后端点。  
6. 无 Alembic；不在本切片做多 IdP 管理 UI。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 多 IdP 联邦管理 UI  
- Discovery → JWT JWKS 接线（Foundation 见 ADR-0067 / PHX-G48）  
- Refresh / RP-Logout  

## 关联

- [ADR-0058-oidc-authorization-code-login.md](ADR-0058-oidc-authorization-code-login.md)
- [../project/PHX-G47_ARCHITECTURE_GATE.md](../project/PHX-G47_ARCHITECTURE_GATE.md)
