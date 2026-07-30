# PHX-G176 OpenAPI Platform Status-Code Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0195  
**授权：** DAL-G003 + DAL-G004（DAL-U049）

## 1. 门禁目标

诚实文档化 Platform IdP/Roles 写路径已发出的命名 HTTP 状态码。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | platform.openapi.yaml `1.0.2` |
| Codes | 400 / 404 / 409 / 503 named + GatewayDetailError |
| Inventory | PHX-G176；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0195 + OpenAPI + inventory/ops + tests + DAL-U049 + tip/status 齐。  
