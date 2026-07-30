# PHX-G180 OpenAPI Package/Terminal/Knowledge Status-Code Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0199  
**授权：** DAL-G003 + DAL-G004（DAL-U053）

## 1. 门禁目标

诚实文档化 Package / Terminal / Knowledge 网关已发出的命名 HTTP 状态码。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contracts | package `1.0.3`；terminal `1.1.3`；knowledge `1.0.3` |
| Codes | Named 400/403/404/409/503 + GatewayDetailError |
| Inventory | PHX-G180；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0199 + OpenAPI + inventory/ops + tests + DAL-U053 + tip/status 齐。  
