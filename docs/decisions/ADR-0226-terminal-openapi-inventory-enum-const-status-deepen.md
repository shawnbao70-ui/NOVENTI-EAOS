# ADR-0226 — Terminal OpenAPI Inventory Enum-Const Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G207  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U080**；PO cue「充分授权…自主开发…加快」

## 背景

G205 已展示 fields-shape；G206 闭合 catalog 单值 enum const。
Admin 仍需一瞥看到 single-enum const honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `single_enum_const` 时追加 `single-enum const honest (G206/G207)`。  
2. Admin CTA **OpenAPI inventory status (G207)**。  
3. Inventory **不** bump（对标 G203/G205 UI-only）。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Per-code exhaustive details shapes  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G207_ARCHITECTURE_GATE.md](../project/PHX-G207_ARCHITECTURE_GATE.md)  
