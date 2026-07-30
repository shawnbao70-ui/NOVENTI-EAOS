# PHX-G188 OpenAPI JWT Status Body Field Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Auth / OpenAPI  
**规范源：** ADR-0207  
**授权：** DAL-G003 + DAL-G004（DAL-U061）

## 1. 门禁目标

诚实文档化 `GET /auth/jwt/status` body 与 `jwt_status_view()` emit 对齐。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Contract | auth `1.3.11` |
| Schemas | JwtStatusData / JwtDenylistPosture field parity |
| Inventory | PHX-G188；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0207 + OpenAPI + inventory/ops + tests + DAL-U061 + tip/status 齐。  
