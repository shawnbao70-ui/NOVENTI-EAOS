# PHX-G175 Terminal Host-Acquire Status Surface Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Admin  
**规范源：** ADR-0194  
**授权：** DAL-G003 + DAL-G004（DAL-U048）

## 1. 门禁目标

将 G173 host-acquire 产品姿态投影到 Terminal Admin 可读摘要。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Source | `GET /v1/marketplace/status` → `host_acquire_product` |
| UI | Status CTA + `#hostAcquireStatus` line |
| Auto | Boot after demo bootstrap；post host-acquire refresh |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0194 + UI + tests + DAL-U048 + tip/status 齐。  
