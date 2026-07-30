# PHX-G67 Tenant IdP Federation SQL Adapter Architecture Gate

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0086  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选 SQL 仓储持久化租户联邦绑定；默认 memory。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_TENANT_IDP_FEDERATION_STORE` |
| Default | `memory` |
| Schema | Alembic `0027` `kernel.tenant_idp_bindings` |
| URL | fail-closed `postgresql+psycopg` |

## 3. Exit Criteria

1. ADR-0086 Accepted。  
2. sql/memory 可切换；契约绿；head `0027`。  
3. 全量 contracts 绿；包 `0.2.0`。  

见 [PHX-G67_ACCEPTANCE.md](PHX-G67_ACCEPTANCE.md)。
