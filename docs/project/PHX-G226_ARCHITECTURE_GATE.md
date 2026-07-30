# PHX-G226 OpenAPI HostAcquirePayload Named Honesty Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** OpenAPI Inventory  
**规范源：** ADR-0245  
**授权：** DAL-G003 + DAL-G004（DAL-U099）

## 1. 门禁目标

将 HostAcquireResult.data 嵌套匿名体提升为 named HostAcquirePayload。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Schema-only named payload |
| Inventory | G226 / ops 1.0.39 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0245 + OpenAPI + inventory + tests + DAL-U099 + tip/status 齐。  
