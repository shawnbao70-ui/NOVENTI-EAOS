# PHX-G216 OpenAPI ErrorResponse.details Description-Key Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0235  
**授权：** DAL-G003 + DAL-G004（DAL-U089）

## 1. 门禁目标

消除 ErrorResponse.details 重复 description 键导致的 known-shape 文案静默丢失。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Schema-only honesty（4 domains） |
| Inventory | G216 / ops 1.0.34 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0235 + OpenAPI + inventory + tests + DAL-U089 + tip/status 齐。  
