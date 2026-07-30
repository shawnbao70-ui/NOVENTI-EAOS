# PHX-G90 Declared EAOS Roles Catalog SQL Store Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Permission  
**规范源：** ADR-0109  
**人工确认：** 支付清算另批；无自动写 grant / WebAuthn 产品页  

## 1. 门禁目标

声明角色 memory|sql 持久化 + 平台 CRUD；租户聚合只读。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Env | `EAOS_ROLE_CATALOG_STORE` |
| Schema | Alembic `0029` |
| Platform | `/v1/platform/roles` |
| Tenant | `/v1/permission/roles` 只读 |

## 3. Exit Criteria

1. ADR-0109 Accepted。  
2. memory 默认；sql round-trip；disable 不进租户聚合。  
3. 全量 contracts 绿；包 `0.2.0`；head `0029`。  

见 [PHX-G90_ACCEPTANCE.md](PHX-G90_ACCEPTANCE.md)。
