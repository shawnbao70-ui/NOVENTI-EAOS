# PHX-G80 OIDC amr/acr Auth Context Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0099  
**人工确认：** 支付清算另批；无 MFA 注册 UI / social login  

## 1. 门禁目标

可选 `amr`/`acr` 认证上下文；默认关闭；mint 路径 fail-closed。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_OIDC_REQUIRED_AMR` / `EAOS_OIDC_REQUIRED_ACR` |
| Hook | `map_oidc_claims_to_eaos`（在 G79 之后） |
| Status | `required_amr*` / `required_acr*` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0099 Accepted。  
2. 不匹配 deny；匹配 mint；status 可观测。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G80_ACCEPTANCE.md](PHX-G80_ACCEPTANCE.md)。
