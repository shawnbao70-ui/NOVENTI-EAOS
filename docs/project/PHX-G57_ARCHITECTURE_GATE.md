# PHX-G57 IdP Registry SQL Adapter Architecture Gate

**日期：** 2026-07-19  
**状态：** Fully Accepted（Foundation）  
 
**归属：** Platform API Gateway / Persistence  
**规范源：** ADR-0076  
**人工确认：** 支付清算另批  

## 1. 门禁目标

可选 SQL 仓储接线 `kernel.idp_issuer_bindings`；默认 memory。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Switch | `EAOS_IDP_REGISTRY_STORE` |
| Default | `memory` |
| SQL URL | fail-closed `postgresql+psycopg` |
| Schema | 复用 Alembic `0025` |

## 3. Exit Criteria

1. ADR-0076 Accepted。  
2. sql/memory 可切换；契约绿；无新 migration。  
3. 全量 contracts 绿；包版本仍 `0.2.0`。  

见 [PHX-G57_ACCEPTANCE.md](PHX-G57_ACCEPTANCE.md)；契约 `505 passed`。
