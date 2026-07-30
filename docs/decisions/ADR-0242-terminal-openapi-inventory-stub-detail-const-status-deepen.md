# ADR-0242 — Terminal OpenAPI Inventory Stub Detail Const Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G223  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U096**；PO cue「充分授权…自主开发…加快」

## 背景

G221 已展示 cross-domain elevation $ref；G222 闭合 Payment/WebAuthn stub
detail const。Admin 仍需一瞥看到 stub detail const honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `stub_detail_const` 时追加 `stub detail const honest (G222/G223)`。  
2. Admin CTA **OpenAPI inventory status (G223)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G223_ARCHITECTURE_GATE.md](../project/PHX-G223_ARCHITECTURE_GATE.md)  
