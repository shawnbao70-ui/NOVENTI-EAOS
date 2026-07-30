# PHX-G195 OpenAPI RoleCatalogStatus source_counts Field Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Permission OpenAPI / Inventory  
**规范源：** ADR-0214  
**授权：** DAL-G003 + DAL-G004（DAL-U068）

## 1. 门禁目标

诚实对齐 `RoleCatalogStatus.source_counts` / `catalog_store` 与 runtime emit，
不打开 Role→grant mint 或 Cap→grant。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Schema | `RoleCatalogSourceCounts` field parity |
| catalog_store | enum `process_memory` |
| Inventory | PHX-G195 / ops 1.0.21 |
| HARD HOLDS | Cap≠grant；Brain/Twin/PSP closed |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0214 + OpenAPI + inventory/ops + contracts + DAL-U068 + tip/status 齐。  
