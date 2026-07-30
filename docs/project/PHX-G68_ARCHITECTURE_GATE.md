# PHX-G68 JWT Tenant IdP Federation Enforcement Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway  
**规范源：** ADR-0087  
**人工确认：** 支付清算另批  

## 1. 门禁目标

租户面 JWT 与 OIDC 共用联邦强制；平台面与开发头不强制。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | 复用 `EAOS_TENANT_IDP_FEDERATION` |
| Hook | `context_from_tenant_claims` |
| Issuer | `eaos_oidc_issuer` 优先，否则非 EAOS `iss` |
| Non-goal | 平台面强制 / UI |

## 3. Exit Criteria

1. ADR-0087 Accepted。  
2. 无绑定 JWT 403；有绑定放行；契约绿。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G68_ACCEPTANCE.md](PHX-G68_ACCEPTANCE.md)。
