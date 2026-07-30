# PHX-G189 OpenAPI IdP Status Body Field Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / OpenAPI  
**规范源：** ADR-0208  
**授权：** DAL-G003 + DAL-G004（DAL-U062）

## 1. 门禁目标

诚实文档化 `GET /auth/idp/status` 顶层与 jwt/registry/federation 聚合形状。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | auth `1.3.12` |
| Schemas | IdpStatusData + aggregates；oidc nested open |
| Inventory | PHX-G189；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0208 + OpenAPI + inventory/ops + tests + DAL-U062 + tip/status 齐。  
