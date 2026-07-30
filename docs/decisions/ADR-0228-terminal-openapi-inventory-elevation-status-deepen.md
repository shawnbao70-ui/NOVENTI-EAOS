# ADR-0228 — Terminal OpenAPI Inventory Elevation Per-Code Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G209  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U082**；PO cue「充分授权…自主开发…加快」

## 背景

G207 已展示 enum-const；G208 闭合 elevation per-code details schema。
Admin 仍需一瞥看到 elevation details per-code honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `elevation_details_code` 时追加 `elevation details per-code honest (G208/G209)`。  
2. Admin CTA **OpenAPI inventory status (G209)**。  
3. Inventory **不** bump（对标 G203/G205/G207 UI-only）。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Exhaustive per-code details map  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G209_ARCHITECTURE_GATE.md](../project/PHX-G209_ARCHITECTURE_GATE.md)  
