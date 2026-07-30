# ADR-0074 — Multi-IdP Status UI (Foundation, Read-Only)

**状态：** Accepted  
**日期：** 2026-07-19  
**里程碑：** PHX-G55  
**归属：** Platform API Gateway / Smart Terminal interaction boundary

## 背景

G45–G48 已支持多发行方 JWKS、OIDC Discovery 与 JWKS wire，配置仍为环境变量。运维需要在 Terminal Admin 面只读查看 IdP/JWT 状态；不得引入可写 IdP 注册表或绕过 BOOK23。

## 决策

1. 新增只读聚合：`GET /v1/auth/idp/status`，组合 `oidc_status()` 与**脱敏** JWT 发行方摘要。  
2. JWT 摘要可含：`issuer`、`jwks_url`、`has_jwks_json`、`multi_issuer`、`require_jwt`、`allow_dev_headers`、`denylist_enabled`、`has_secret`；**永不**返回 `EAOS_JWT_SECRET`、完整 JWKS JSON、OIDC `client_secret`。  
3. 响应声明 `writable: false`、`config_source: environment`。  
4. Terminal Admin 增加 “IdP / JWT status” 探针按钮；无表单、无 CRUD。  
5. 无 Alembic；不 bump 包版本（仍 `0.2.0`）。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 多 IdP 写注册表（Foundation 见 ADR-0075 / PHX-G56）；Discovery 写回 env 仍延后  
- Refresh / RP-Logout / 社交登录 / 组织级联邦策略 UI  
- Service Mesh / KEDA / 多区域  

## 关联

- [ADR-0058-oidc-authorization-code-login.md](ADR-0058-oidc-authorization-code-login.md)
- [ADR-0064-jwt-multi-issuer-jwks.md](ADR-0064-jwt-multi-issuer-jwks.md)
- [ADR-0066-oidc-discovery.md](ADR-0066-oidc-discovery.md)
- [ADR-0075-multi-idp-write-registry.md](ADR-0075-multi-idp-write-registry.md)
- [../project/PHX-G55_ARCHITECTURE_GATE.md](../project/PHX-G55_ARCHITECTURE_GATE.md)
- [../constitution/BOOK23.md](../constitution/BOOK23.md)
