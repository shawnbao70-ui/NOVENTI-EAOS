# PHX-G184 Terminal OpenAPI Inventory Posture Deepen Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal  
**规范源：** ADR-0203  
**授权：** DAL-G003 + DAL-G004（DAL-U057）

## 1. 门禁目标

Terminal 可见当前 OpenAPI inventory tip（milestone / t0188_status）。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Source | `GET /v1/adapters` meta.openapi_inventory_product |
| UI | Posture line + Refresh CTA |
| full_openapi_http_complete | Remains false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0203 + UI + tests + DAL-U057 + tip/status 齐。  
