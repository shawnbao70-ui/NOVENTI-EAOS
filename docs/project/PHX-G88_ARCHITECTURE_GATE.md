# PHX-G88 Opt-in EAOS Roles Catalog Gate Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission  
**规范源：** ADR-0107  
**人工确认：** 支付清算另批；无 Role 表 / 自动写 grant / MFA 注册  

## 1. 门禁目标

只读聚合 EAOS 角色目录；默认空；不触碰 Kernel 授权写入。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | 可选 `EAOS_ROLE_CATALOG` |
| API | `GET /v1/permission/roles` |
| 来源 | catalog + oidc_map + grant_map |
| Schema | 无 Alembic |

## 3. Exit Criteria

1. ADR-0107 Accepted。  
2. 空配置空目录；聚合来源正确；不写 grants。  
3. 全量 contracts 绿；包 `0.2.0`；head `0028`。  

见 [PHX-G88_ACCEPTANCE.md](PHX-G88_ACCEPTANCE.md)。
