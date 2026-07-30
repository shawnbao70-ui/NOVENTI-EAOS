# PHX-G183 Terminal Payment-Clearing Status Surface Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Admin  
**规范源：** ADR-0202  
**授权：** DAL-G003 + DAL-G004（DAL-U056）

## 1. 门禁目标

Admin 一瞥确认 payment-clearing product posture（default OFF；≠ external PSP）。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Admin CTA + status line |
| Source | `GET /marketplace/status` → `payment_clearing_product` |
| PSP | Remains false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0202 + Terminal UI + tests + DAL-U056 + tip/status 齐。  
