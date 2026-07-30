# PHX-G187 OpenAPI OIDC Login Product-Posture Schema Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / OpenAPI  
**规范源：** ADR-0206  
**授权：** DAL-G003 + DAL-G004（DAL-U060）

## 1. 门禁目标

诚实文档化 `oidc_login_product` GET body 与运行时 emit 对齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | auth `1.3.10` |
| Schema | OidcLoginProductPosture field parity |
| Inventory | PHX-G187；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0206 + OpenAPI + inventory/ops + tests + DAL-U060 + tip/status 齐。  
