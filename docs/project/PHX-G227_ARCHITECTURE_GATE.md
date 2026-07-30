# PHX-G227 Terminal OpenAPI Inventory HostAcquirePayload Status Deepen Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0246  
**授权：** DAL-G003 + DAL-G004（DAL-U100）

## 1. 门禁目标

Terminal strip 表面化 G226 HostAcquirePayload 状态（无 inventory bump）。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Admin CTA + strip marker |
| Inventory | 不 bump（仍 G226） |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0246 + UI + tests + DAL-U100 + tip/status 齐。  
