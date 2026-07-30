# ADR-0166 — OIDC Login Product Surface (Thin)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G147  
**归属：** API Gateway / Auth / Smart Terminal  
**授权：** DAL-G003 charter-safe continuous autonomy（DAL-U008）

## 背景

T-0189 将「OIDC 登录页」标为延后。既有 G40/G61/G132 已交付 Authorization Code login/callback/providers 与 refresh/logout；运营面缺少命名的 **OIDC Login Product** 姿态与 Terminal 产品面板。本切片不引入新认证协议。

## 决策

1. 新增只读 helper `api/gateway/oidc_login_product.py`，返回 Foundation OIDC 登录产品姿态：  
   - `authorization_code_enabled` 来自既有 OIDC 配置（`OidcSettings.enabled`）  
   - `live_routes` 列出 Auth Code 产品路径（status/login/callback/providers/refresh/logout）  
   - `fail_closed_when_unconfigured: true`；未配置时 `fail_closed=true`（login/callback 仍 503）  
2. 将姿态挂到 `oidc_status()` → `GET /v1/auth/oidc/status` 的 `oidc_login_product` 字段（additive；不破坏 G145 `webauthn_product`）。  
3. OpenAPI `auth.openapi.yaml` 文档化姿态字段；`info.version` patch bump（1.3.1 → 1.3.2）。  
4. Terminal 命名「OIDC Login Product」面板：展示姿态 + 复用既有 Login/Refresh/Logout/providers CTA。  
5. **不**新增认证协议；**不**实现 WebAuthn ceremony；**不**打开 Role→grant mint；**不**新增 Alembic；包版本保持 `0.2.1`。

## Explicit Out（本切片不开口）

- 新 OAuth/OIDC 协议变体或隐式流  
- Live WebAuthn registration ceremony  
- Role→grant auto-write / mint from role  
- Marketplace 支付清算 / 外部仲裁  
- Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- T-0189「OIDC 登录页延后」以 **thin product surface** 关闭（相对面仍是 G40/G61/G132 Auth Code）。  
- Eng 下一可选加深仍为 WebAuthn ceremony / Role→grant auto-write；支付清算（`4`）仍暂缓。  
- 未配置 OIDC 仍 fail-closed（503）。

## 关联

- [../project/PHX-G147_ARCHITECTURE_GATE.md](../project/PHX-G147_ARCHITECTURE_GATE.md)  
- [../project/PHX-G147_ACCEPTANCE.md](../project/PHX-G147_ACCEPTANCE.md)  
- [ADR-0058-oidc-authorization-code-login.md](ADR-0058-oidc-authorization-code-login.md)  
- [ADR-0164-webauthn-mfa-product-posture.md](ADR-0164-webauthn-mfa-product-posture.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
