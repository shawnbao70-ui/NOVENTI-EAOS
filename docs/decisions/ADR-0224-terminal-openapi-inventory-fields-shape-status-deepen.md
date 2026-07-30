# ADR-0224 — Terminal OpenAPI Inventory Fields-Shape Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G205  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U078**；PO cue「充分授权…自主开发…加快」

## 背景

G203 已一瞥展示 ErrorBody.details inventory closed；G204 闭合 catalog
`details.fields[]` known-shape。Admin 仍需看到 fields-shape honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `error_details_fields` 时追加 `details.fields[] known-shape honest (G204/G205)`。  
2. Admin CTA **OpenAPI inventory status (G205)**；Operator refresh 文案更新。  
3. Bootstrap quiet refresh 保持。  
4. Inventory **不** bump（对标 G194/G201/G203 UI-only）。  
5. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Per-code exhaustive details enum  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G205_ARCHITECTURE_GATE.md](../project/PHX-G205_ARCHITECTURE_GATE.md)  
