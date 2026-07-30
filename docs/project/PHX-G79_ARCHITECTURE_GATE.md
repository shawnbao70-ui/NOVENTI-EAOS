# PHX-G79 OIDC Required Claims Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0098  
**人工确认：** 支付清算另批；无 MFA / social login / claim→role  

## 1. 门禁目标

可选 id_token 必填声明；默认关闭；mint 路径 fail-closed。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_OIDC_REQUIRED_CLAIMS` |
| Hook | `map_oidc_claims_to_eaos` |
| Status | `required_claims` / `required_claims_enabled` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0098 Accepted。  
2. 缺声明 deny；齐全 mint；status 可观测。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G79_ACCEPTANCE.md](PHX-G79_ACCEPTANCE.md)。
