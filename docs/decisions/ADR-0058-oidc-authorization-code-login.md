# ADR-0058 — OIDC Authorization Code Login (Foundation)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G40  
**归属：** Platform API Gateway / Identity boundary

## 背景

G37/G38 已支持 Bearer JWT（HS256/RS256）。仍缺 Authorization Code 登录入口。Gateway 须在认证边界完成 IdP 回调并签发 EAOS 受信 JWT；body 仍不可提升。

## 决策

1. 路由（Gateway 认证边界）：  
   - `GET /v1/auth/oidc/status`  
   - `GET /v1/auth/oidc/login` → 302 IdP（PKCE S256）  
   - `GET /v1/auth/oidc/callback` → code 交换 → 签发 EAOS HS256 JWT  
2. 配置：`EAOS_OIDC_*`（issuer、client_id、client_secret、redirect_uri、authorize/token URL 或 discovery）。  
3. Claims：IdP `sub` → EAOS `sub`（非 UUID 时用 UUID5 稳定映射）；`eaos_tenant_id` 或 `EAOS_OIDC_DEFAULT_TENANT_ID`。  
4. Terminal UI 可携带 `Authorization: Bearer`；开发头路径仍可用。  
5. 未配置 OIDC 时 login/callback 返回 503（非 fail-open）。

## Explicit Defer

- Refresh token / logout RP  
- 多 IdP 联邦管理 UI（Foundation Discovery 见 ADR-0066 / PHX-G47）  
- 社交登录与组织级 IdP 联邦策略 UI  

## 关联

- [ADR-0053-jwt-oidc-trusted-context.md](ADR-0053-jwt-oidc-trusted-context.md)
- [ADR-0055-jwt-jwks-rs256.md](ADR-0055-jwt-jwks-rs256.md)
- [ADR-0066-oidc-discovery.md](ADR-0066-oidc-discovery.md)
- [../project/PHX-G40_ARCHITECTURE_GATE.md](../project/PHX-G40_ARCHITECTURE_GATE.md)
