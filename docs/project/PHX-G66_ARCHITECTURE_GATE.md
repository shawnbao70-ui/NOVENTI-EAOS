# PHX-G66 Tenant IdP Federation Binding Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway  
**规范源：** ADR-0085  
**人工确认：** 支付清算另批  

## 1. 门禁目标

租户↔issuer 绑定薄 API + 可选 OIDC fail-closed；默认关闭强制。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Store | 进程内存（Foundation） |
| Plane | Platform only |
| Switch | `EAOS_TENANT_IDP_FEDERATION` |
| Enforce | OIDC map claims 后 |
| Non-goal | UI / SQL / JWT 强制 |

## 3. Exit Criteria

1. ADR-0085 Accepted。  
2. List/bind/unbind 契约绿；强制开关可测。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G66_ACCEPTANCE.md](PHX-G66_ACCEPTANCE.md)。
