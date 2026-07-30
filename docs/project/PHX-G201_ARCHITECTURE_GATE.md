# PHX-G201 Terminal Role Catalog Status Surface Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Admin  
**规范源：** ADR-0220  
**授权：** DAL-G003 + DAL-G004（DAL-U074）

## 1. 门禁目标

Admin/Operator 一瞥展示 Role catalog + Cap≠grant 围栏，不发明 mint 轨。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface | Operator strip + Admin CTA/status |
| Probe | GET /permission/roles/status |
| HARD HOLDS | Cap≠grant；always-on mint closed |
| Inventory | Unchanged（G200 tip） |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0220 + Terminal UI + tests + DAL-U074 + tip/status 齐。  
