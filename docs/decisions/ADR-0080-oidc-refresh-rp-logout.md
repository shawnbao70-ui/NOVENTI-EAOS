# ADR-0080 — OIDC Refresh + RP-Logout (Foundation)

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G61  
**归属：** Platform API Gateway / Identity boundary

## 背景

G40 仅交付 Authorization Code 登录与 EAOS HS256 签发。运维需要可选 Refresh 与 RP-Logout，且不引入组织级联邦策略 UI。

## 决策

1. Opt-in：`EAOS_OIDC_REFRESH=1`；登录时若 IdP 返回 `refresh_token`，按 EAOS `jti` 进程内绑定（不回传 refresh_token 给浏览器）。  
2. `POST /v1/auth/oidc/refresh`：校验 Bearer → IdP `grant_type=refresh_token` → 重签 EAOS JWT；旧 `jti` runtime revoke。  
3. Opt-in：`EAOS_OIDC_RP_LOGOUT=1`；`POST /v1/auth/oidc/logout` 本地 revoke `jti`，并可选返回 Discovery/`EAOS_OIDC_END_SESSION_ENDPOINT` 的 `end_session_url`。  
4. `EAOS_OIDC_POST_LOGOUT_REDIRECT_URI` 可选；status 暴露 refresh/rp_logout/end_session 就绪字段（脱敏）。  
5. Terminal 薄按钮：OIDC Refresh / Logout；无联邦 CRUD。  
6. 无 Alembic；包版本仍 `0.2.0`；支付清算另批。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 组织级联邦策略 UI / social login  
- Refresh token 持久化到 SQL  
- 多区域 / 网格 CRD  

## 关联

- [ADR-0058-oidc-authorization-code-login.md](ADR-0058-oidc-authorization-code-login.md)
- [ADR-0065-jwt-denylist.md](ADR-0065-jwt-denylist.md)
- [../project/PHX-G61_ARCHITECTURE_GATE.md](../project/PHX-G61_ARCHITECTURE_GATE.md)
