# PHX-G204 OpenAPI Error Details fields[] Known-Shape Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0223  
**授权：** DAL-G003 + DAL-G004（DAL-U077）

## 1. 门禁目标

诚实文档化 elevation `details.fields[]`，不关闭其他 details 键。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| details.fields | optional string[] |
| additionalProperties | true（保留） |
| Inventory | PHX-G204 / ops 1.0.28 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0223 + catalog patch + inventory + contracts + DAL-U077 + tip/status 齐。  
