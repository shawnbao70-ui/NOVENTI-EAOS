# PHX-G69 Tenant IdP Federation Terminal Ops Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Platform API Gateway  
**规范源：** ADR-0088  
**人工确认：** 支付清算另批  

## 1. 门禁目标

Terminal Admin 薄操作复用联邦 API；platform 上下文；无策略矩阵 UI。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Admin panel fields + buttons |
| APIs | 既有 G66 federation routes |
| Auth | `platform: true` |
| Tenant | Path via `#fedTenantId`；body 禁 `tenant_id` |

## 3. Exit Criteria

1. ADR-0088 Accepted。  
2. UI/资产/契约绿；无 Alembic。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G69_ACCEPTANCE.md](PHX-G69_ACCEPTANCE.md)。
