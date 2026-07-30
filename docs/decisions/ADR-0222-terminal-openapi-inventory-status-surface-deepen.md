# ADR-0222 — Terminal OpenAPI Inventory Status Surface Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G203  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U076**；PO cue「充分授权…自主开发…加快」

## 背景

G184 已提供 OpenAPI inventory strip；G202 闭合 ErrorBody.details inventory。
Admin 仍需一瞥式看到 tip milestone / t0188 / full_http_complete=false 与
details-closed 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：Admin status 行 +
   ErrorBody.details closed 标记（当 t0188 含 `errorbody_details`）。  
2. Admin CTA **OpenAPI inventory status (G203)**。  
3. Bootstrap quiet refresh。  
4. Inventory **不** bump（对标 G194/G201 UI-only）。  
5. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G203_ARCHITECTURE_GATE.md](../project/PHX-G203_ARCHITECTURE_GATE.md)  
