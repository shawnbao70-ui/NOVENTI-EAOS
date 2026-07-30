# PHX-G173 Marketplace Host-Acquire Status Posture Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Marketplace Gateway  
**规范源：** ADR-0192  
**授权：** DAL-G003 + DAL-G004（DAL-U046）

## 1. 门禁目标

在 Marketplace status 中诚实暴露 G172 host-acquire 产品边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Field | `host_acquire_product` on `GET /marketplace/status` |
| Scripts / install / PSP | All false / fail-closed |
| OpenAPI | marketplace `1.2.3` |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0192 + status field + OpenAPI + tests + DAL-U046 + tip/status 齐。  
