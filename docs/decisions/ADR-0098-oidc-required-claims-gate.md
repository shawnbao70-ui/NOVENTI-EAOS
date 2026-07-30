# ADR-0098 — OIDC Required Claims Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G79  
**归属：** Platform API Gateway / OIDC boundary

## 背景

G66–G78 覆盖联邦绑定、矩阵与 issuer 优先级。OIDC mint 路径仅强制 `sub` / 租户映射，缺少可配置的 id_token 必填声明门禁。

## 决策

1. `EAOS_OIDC_REQUIRED_CLAIMS`：逗号分隔声明名；空/未设 = 关闭。  
2. 在 `map_oidc_claims_to_eaos` 中校验：每个声明必须存在且非空（字符串去空白后非空；`bool` 只要存在即过；容器非空；数值含 `0` 即过）。  
3. 缺失 → `401` + `GATEWAY_OIDC_REQUIRED_CLAIM_MISSING`。  
4. `GET /v1/auth/oidc/status` 暴露 `required_claims` 与 `required_claims_enabled`（无密钥）。  
5. 适用于 callback 与 refresh（当返回 id_token 并 remap 时）；无 Alembic；包版本仍 `0.2.0`。  
6. 非目标：claim→角色映射、MFA/`amr`/`acr`、social login、多 issuer 登录重定向。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Claim→role / group 映射表  
- MFA 注册 UI / 完整策略引擎（amr/acr 门禁见 ADR-0099）  
- Social login / OIDC 多 issuer 登录重定向  

## 关联

- [ADR-0058-oidc-login.md](ADR-0058-oidc-login.md)（若存在；否则见 OIDC G40 族）
- [ADR-0097-tenant-idp-federation-issuer-priority.md](ADR-0097-tenant-idp-federation-issuer-priority.md)
- [../project/PHX-G79_ARCHITECTURE_GATE.md](../project/PHX-G79_ARCHITECTURE_GATE.md)
