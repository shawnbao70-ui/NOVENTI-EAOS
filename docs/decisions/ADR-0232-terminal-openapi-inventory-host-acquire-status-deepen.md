# ADR-0232 — Terminal OpenAPI Inventory Host-Acquire Details Status Deepen

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G213  
**归属：** Smart Terminal / Admin  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U086**；PO cue「充分授权…自主开发…加快」

## 背景

G211 已展示 OIDC details；G212 闭合 host-acquire package_key details。
Admin 仍需一瞥看到 host-acquire details per-code honest 标记。

## 决策

1. 加深 `loadOpenapiInventoryProductPosture({ quiet })`：当 t0188 含
   `host_acquire_details` 时追加 `host-acquire details per-code honest (G212/G213)`。  
2. Admin CTA **OpenAPI inventory status (G213)**。  
3. Inventory **不** bump。  
4. 包 `0.2.1`；Alembic `0029`；`full_openapi_http_complete` 仍 false。

## Explicit Out

- Non-allowlist catalog  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G213_ARCHITECTURE_GATE.md](../project/PHX-G213_ARCHITECTURE_GATE.md)  
