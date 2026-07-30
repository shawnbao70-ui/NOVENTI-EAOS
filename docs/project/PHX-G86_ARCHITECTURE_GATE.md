# PHX-G86 OIDC Provider End-Session Catalog Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0105  
**人工确认：** 支付清算另批；无 MFA 注册 / Role 目录  

## 1. 门禁目标

可选 provider 级 `end_session_endpoint`；缺省回落主 OIDC。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `LOGIN_PROVIDERS` 第 7 段 |
| Logout | provider end_session > primary |
| Catalog | `has_end_session` / `end_session_endpoint` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0105 Accepted。  
2. 有 end_session 的 provider logout 指对端；无则回落。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G86_ACCEPTANCE.md](PHX-G86_ACCEPTANCE.md)。
