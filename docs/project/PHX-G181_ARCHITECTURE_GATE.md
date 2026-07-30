# PHX-G181 OpenAPI AI/Event/Brain/Marketplace Status-Code Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0200  
**授权：** DAL-G003 + DAL-G004（DAL-U054）

## 1. 门禁目标

诚实文档化 AI / Event / Twin·Brain / Marketplace 网关已发出的命名 HTTP 状态码。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contracts | ai/event/brain `1.0.3`；marketplace `1.2.5` |
| Codes | Named 400/403/404/409/503 + GatewayDetailError |
| HARD HOLDS | Twin authorize / Brain execute remain fail-closed 403 |
| Inventory | PHX-G181；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0200 + OpenAPI + inventory/ops + tests + DAL-U054 + tip/status 齐。  
