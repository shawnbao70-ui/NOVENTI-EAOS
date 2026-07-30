# ADR-0240 — Terminal OpenAPI Inventory Cross-Domain Elevation $ref Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G221  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U094**；PO cue「充分授权…自主开发…加快」

## 背景

G219 已展示 named Details $ref；G220 闭合十域 elevation details `$ref`。
Admin 仍需一瞥看到 cross-domain elevation $ref 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `cross_domain_elevation_details_ref` 时追加
   `cross-domain elevation details $ref honest (G220/G221)`。  
2. Admin CTA **OpenAPI inventory status (G221)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G221_ARCHITECTURE_GATE.md](../project/PHX-G221_ARCHITECTURE_GATE.md)  
