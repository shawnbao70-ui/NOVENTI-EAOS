# PHX-G185 OpenAPI Auth/Permission Product-Posture Schema Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0204  
**授权：** DAL-G003 + DAL-G004（DAL-U058）

## 1. 门禁目标

诚实文档化 Auth/Permission product-posture GET body 与运行时 emit 对齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contracts | auth `1.3.9`；permission `1.1.7` |
| Schemas | WebauthnProductPosture / RoleGrantProductPosture field parity |
| Inventory | PHX-G185；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0204 + OpenAPI + inventory/ops + tests + DAL-U058 + tip/status 齐。  
