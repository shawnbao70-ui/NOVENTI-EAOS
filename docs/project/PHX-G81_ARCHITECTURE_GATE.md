# PHX-G81 OIDC Claim→Role JWT Mint Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0100  
**人工确认：** 支付清算另批；无 social login / MFA 注册 / Permission sync  

## 1. 门禁目标

可选 IdP claim→`eaos_roles` mint；默认关闭；不触碰 Kernel 授权。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `ROLE_CLAIM` + `ROLE_MAP` + 可选 `REQUIRE_MAPPED_ROLE` |
| Hook | `map_oidc_claims_to_eaos`（G79/G80 之后） |
| JWT | `eaos_roles` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0100 Accepted。  
2. 映射 mint；可选强制；status 可观测。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G81_ACCEPTANCE.md](PHX-G81_ACCEPTANCE.md)。
