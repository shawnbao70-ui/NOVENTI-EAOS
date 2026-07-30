# PHX-G85 OIDC Per-Provider Refresh Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / OIDC  
**规范源：** ADR-0104  
**人工确认：** 支付清算另批；无 MFA 注册 / provider 级 end_session 目录  

## 1. 门禁目标

多 provider 登录后的 refresh/logout 使用同一 overlay client/token；无 schema 变更。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| 绑定 | JWT `eaos_oidc_login_provider` |
| Refresh | `resolve_login_oidc_settings(claim)` |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0104 Accepted。  
2. Provider 登录 mint claim；refresh 命中 overlay；主路径不变。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G85_ACCEPTANCE.md](PHX-G85_ACCEPTANCE.md)。
