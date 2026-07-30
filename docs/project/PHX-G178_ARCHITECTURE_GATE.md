# PHX-G178 OpenAPI Identity/Org Status-Code Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0197  
**授权：** DAL-G003 + DAL-G004（DAL-U051）

## 1. 门禁目标

诚实文档化 Identity / Organization 网关已发出的命名 HTTP 状态码。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contracts | identity `1.0.3`；organization `1.0.2` |
| Codes | Named 400/403/404/409/503 + GatewayDetailError |
| Mapping | Document-as-emitted（含 known quirks） |
| Inventory | PHX-G178；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0197 + OpenAPI + inventory/ops + tests + DAL-U051 + tip/status 齐。  
