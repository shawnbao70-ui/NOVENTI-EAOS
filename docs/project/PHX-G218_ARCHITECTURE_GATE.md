# PHX-G218 OpenAPI Named Details $ref Composition Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0237  
**授权：** DAL-G003 + DAL-G004（DAL-U091）

## 1. 门禁目标

将已命名 per-code Details schema 通过 anyOf `$ref` 接到 Error*.details。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Schema composition honesty |
| Inventory | G218 / ops 1.0.35 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0237 + OpenAPI + inventory + tests + DAL-U091 + tip/status 齐。  
