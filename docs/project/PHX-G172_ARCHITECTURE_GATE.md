# PHX-G172 Marketplace Listing Host Acquire Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Marketplace / Smart Terminal Extension Host  
**规范源：** ADR-0191  
**授权：** DAL-G003 + DAL-G004（DAL-U045）

## 1. 门禁目标

提供 allowlisted listing→host 投影，完成 Admin 一键联调，且不打开 Marketplace 任意脚本或 HARD HOLDS。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Route | `POST /v1/marketplace/listings/{id}/host-acquire` |
| Allowlist | First-party keys only（`noventi.demo.panel`） |
| Acquire | Technical；idempotent if already acquired |
| Package install | Explicit out |
| Scripts | Never execute Marketplace remote code |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0191 + route + demo seed + UI + tests + DAL-U045 + tip/status 齐；`test_api_gateway_g172_*` 绿。  
