# PHX-G182 Terminal Extensions Host-Path Readiness Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal Extensions  
**规范源：** ADR-0201  
**授权：** DAL-G003 + DAL-G004（DAL-U055）

## 1. 门禁目标

在 Extensions 面板完成 allowlisted demo host-path：readiness + Acquire→Host + `host_actions`，无需跳 Admin。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Extensions panel readiness + CTA |
| Allowlist | Unchanged（`noventi.demo.panel` only） |
| Bootstrap | Milestone PHX-G182；host_actions hint |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0201 + Terminal UI + bootstrap + tests + DAL-U055 + tip/status 齐。  
