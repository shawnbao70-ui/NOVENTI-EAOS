# ADR-0230 — Terminal OpenAPI Inventory OIDC Details Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G211  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U084**；PO cue「充分授权…自主开发…加快」

## 背景

G209 已展示 elevation per-code；G210 闭合 OIDC details schemas。
Admin 仍需一瞥看到 OIDC details per-code honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `oidc_details_code` 时追加 `OIDC details per-code honest (G210/G211)`。  
2. Admin CTA **OpenAPI inventory status (G211)**。  
3. Inventory **不** bump（对标 G203/G205/G207/G209 UI-only）。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Exhaustive per-code details map  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G211_ARCHITECTURE_GATE.md](../project/PHX-G211_ARCHITECTURE_GATE.md)  
