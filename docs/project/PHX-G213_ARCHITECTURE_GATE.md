# PHX-G213 Terminal OpenAPI Inventory Host-Acquire Details Status Deepen Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Admin  
**规范源：** ADR-0232  
**授权：** DAL-G003 + DAL-G004（DAL-U086）

## 1. 门禁目标

一瞥展示 OpenAPI inventory tip（含 G212 host-acquire details），不开放 non-allowlist。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Operator strip deepen + Admin CTA |
| Inventory | Unchanged（G212 tip） |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0232 + Terminal UI + tests + DAL-U086 + tip/status 齐。  
