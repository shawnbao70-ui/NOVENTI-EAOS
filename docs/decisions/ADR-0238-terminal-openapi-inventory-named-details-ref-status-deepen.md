# ADR-0238 — Terminal OpenAPI Inventory Named Details $ref Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G219  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U092**；PO cue「充分授权…自主开发…加快」

## 背景

G217 已展示 description-key；G218 闭合 named Details anyOf `$ref` 组合。
Admin 仍需一瞥看到 named-details $ref composition 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `named_details_ref_composition` 时追加
   `named Details $ref composition honest (G218/G219)`。  
2. Admin CTA **OpenAPI inventory status (G219)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G219_ARCHITECTURE_GATE.md](../project/PHX-G219_ARCHITECTURE_GATE.md)  
