# PHX-G87 OIDC Authorize ACR/Prompt Step-Up Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0106  
**人工确认：** 支付清算另批；无 MFA 注册 UX / WebAuthn  

## 1. 门禁目标

可选在 authorize 请求附加 `acr_values` / `prompt`；默认关闭；与 G80 token 门禁互补。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `AUTHORIZE_ACR_VALUES` / `AUTHORIZE_PROMPT` |
| 挂点 | `begin_oidc_login` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0106 Accepted。  
2. 空配置无附加参数；启用时 authorize 含对应字段；status 可观测。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G87_ACCEPTANCE.md](PHX-G87_ACCEPTANCE.md)。
