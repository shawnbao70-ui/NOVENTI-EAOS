# ADR-0067 — OIDC Discovery → JWT JWKS Wire (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G48  
**归属：** Platform API Gateway / Identity boundary

## 背景

G47 Discovery 已解析 `jwks_uri` 并暴露于 status，但 JWT 校验不消费。G45 已有多发行方 JWKS allowlist。需可选桥接，使 IdP Metadata 的 JWKS 进入校验路径，且不破坏 G40 EAOS HS256 签发。

## 决策

1. Opt-in：`EAOS_OIDC_JWKS_WIRE=1`；需同时启用 OIDC Discovery（`EAOS_OIDC_DISCOVERY`）。  
2. 显式 `EAOS_JWT_ISSUERS_JSON` 或 `EAOS_JWT_JWKS_JSON` / `EAOS_JWT_JWKS_URL` 优先——已配置则接线为 no-op。  
3. 接线时将 Discovery `jwks_uri` 注入为单一 `JwtIssuerBinding`（`issuer=EAOS_OIDC_ISSUER`，`jwks_url=jwks_uri`）；HTTPS（loopback 仅测试）。  
4. 若同时配置 `EAOS_JWT_SECRET` 与 `EAOS_JWT_ISSUER` 且与 OIDC issuer 不同，则将该 EAOS issuer 一并 allowlist（无 JWKS），以保留 G40 HS256 登录令牌。  
5. 缺 `jwks_uri` / Discovery 失败 → fail-closed（Bearer 路径）；仅在校验 Bearer 时解析，不影响开发头路径。  
6. `/v1/auth/oidc/status` 暴露 `jwks_wire`；无 Alembic；无多 IdP UI。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 多 IdP 联邦管理 UI  
- 将 Discovery 结果写回进程环境变量  
- Refresh / RP-Logout  

## 关联

- [ADR-0064-jwt-multi-issuer-jwks.md](ADR-0064-jwt-multi-issuer-jwks.md)
- [ADR-0066-oidc-discovery.md](ADR-0066-oidc-discovery.md)
- [../project/PHX-G48_ARCHITECTURE_GATE.md](../project/PHX-G48_ARCHITECTURE_GATE.md)
