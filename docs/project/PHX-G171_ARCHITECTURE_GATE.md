# PHX-G171 Terminal UuidResult Client Harden Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal UI  
**规范源：** ADR-0190  
**授权：** DAL-G003 + DAL-G004（DAL-U044）

## 1. 门禁目标

Terminal UI 消费 G170 双键 UuidResult，不依赖单一方言。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Helper | `uuidFromResult` → `id` \|\| `data` |
| Scope | Session/Intent/Preview + Admin create IDs + Extension register |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0190 + helper + tests + DAL-U044 + tip/status 齐；`test_api_gateway_g171_*` 绿。  
