# ADR-0236 — Terminal OpenAPI Inventory Error Details Description-Key Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G217  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U090**；PO cue「充分授权…自主开发…加快」

## 背景

G215 已展示 MFA enrollment；G216 闭合 ErrorResponse.details 重复 description 键。
Admin 仍需一瞥看到 description-key honesty 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `error_details_description_key` 时追加
   `ErrorResponse.details description-key honest (G216/G217)`。  
2. Admin CTA **OpenAPI inventory status (G217)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G217_ARCHITECTURE_GATE.md](../project/PHX-G217_ARCHITECTURE_GATE.md)  
