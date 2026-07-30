# ADR-0227 — OpenAPI Elevation Details Per-Code Shape Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G208  
**归属：** OpenAPI Inventory / Terminal  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U081**；PO cue「充分授权…自主开发…加快」

## 背景

Tip Next 列出 per-code `details` shapes。G204 已声明通用 `fields[]`；
live elevation deny 稳定发出 `TERMINAL_CONTEXT_ELEVATION_DENIED` +
`details.fields`，但缺少按码命名的 schema。

## 决策

1. 新增 `ContextElevationDenialDetails`（required `fields: string[]`；
   `additionalProperties: false`）于 **terminal** 与 **ops** OpenAPI。  
2. 明确仅绑定 `TERMINAL_CONTEXT_ELEVATION_DENIED`；不宣称全码穷尽。  
3. terminal **1.1.9**；Inventory `milestone=PHX-G208`；
   `t0188_status=mount_parity_complete_elevation_details_code_shape_honest`；
   ops **1.0.30**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Exhaustive per-code details map across all ERROR_CODES  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G208_ARCHITECTURE_GATE.md](../project/PHX-G208_ARCHITECTURE_GATE.md)  
