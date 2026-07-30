# PHX-G177 OpenAPI Auth OIDC Status-Code Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0196  
**授权：** DAL-G003 + DAL-G004（DAL-U050）

## 1. 门禁目标

诚实文档化 Auth OIDC login/callback/refresh/logout 已发出的命名 HTTP 状态码。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | auth.openapi.yaml `1.3.8` |
| Codes | login 400/503；callback 400/401/403/502/503；refresh 400/401/502/503；logout 400/401/503 |
| Envelope | GatewayDetailError（含 login 503，不再用 ErrorResponse） |
| Inventory | PHX-G177；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0196 + OpenAPI + inventory/ops + tests + DAL-U050 + tip/status 齐。  
