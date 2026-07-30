# ADR-0239 — OpenAPI Cross-Domain Elevation Details $ref Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G220  
**归属：** OpenAPI Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U093**；PO cue「充分授权…自主开发…加快」

## 背景

G218 已在 auth/marketplace/ops/terminal 将 named Details 接到
`Error*.details` anyOf。其余域仍仅扁平 `fields[]`，缺少
`ContextElevationDenialDetails` 的 `$ref` 组合。

## 决策

1. ai/brain/event/identity/knowledge/organization/package/permission/platform/workflow：
   增加（或复用）`ContextElevationDenialDetails`，`Error*.details` 改为 anyOf `$ref`。  
2. Inventory `milestone=PHX-G220`；
   `t0188_status=mount_parity_complete_cross_domain_elevation_details_ref_honest`；
   ops **1.0.36**。  
3. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G220_ARCHITECTURE_GATE.md](../project/PHX-G220_ARCHITECTURE_GATE.md)  
