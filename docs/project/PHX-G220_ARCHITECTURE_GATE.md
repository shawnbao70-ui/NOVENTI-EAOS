# PHX-G220 OpenAPI Cross-Domain Elevation Details $ref Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0239  
**授权：** DAL-G003 + DAL-G004（DAL-U093）

## 1. 门禁目标

十域 Error*.details 通过 anyOf `$ref` 接到 ContextElevationDenialDetails。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Schema composition honesty |
| Inventory | G220 / ops 1.0.36 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0239 + OpenAPI + inventory + tests + DAL-U093 + tip/status 齐。  
