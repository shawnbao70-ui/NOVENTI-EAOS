# PHX-G190 OpenAPI OIDC Status Body Field Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / OpenAPI  
**规范源：** ADR-0209  
**授权：** DAL-G003 + DAL-G004（DAL-U063）

## 1. 门禁目标

诚实文档化 `GET /auth/oidc/status` 与 IdP nested `oidc` 相对 `oidc_status()` emit。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | auth `1.3.13` |
| Schemas | OidcStatusData field parity；IdP.oidc $ref |
| Inventory | PHX-G190；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0209 + OpenAPI + inventory/ops + tests + DAL-U063 + tip/status 齐。  
