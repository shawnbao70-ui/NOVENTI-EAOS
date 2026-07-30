# PHX-G202 OpenAPI ErrorBody/ErrorResponse Details Inventory Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0221  
**授权：** DAL-G003 + DAL-G004（DAL-U075）

## 1. 门禁目标

闭合 catalog 内 ErrorResponse/ErrorBody 的 `details` 文档缺口，对齐 live emit。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Gap domains | auth / permission / org / workflow / platform |
| Inventory | PHX-G202 / ops 1.0.27 |
| full_openapi_http_complete | false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0221 + OpenAPI + inventory + scan contract + DAL-U075 + tip/status 齐。  
