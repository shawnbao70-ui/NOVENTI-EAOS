# ADR-0223 — OpenAPI Error Details fields[] Known-Shape Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G204  
**归属：** OpenAPI Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U077**；PO cue「充分授权…自主开发…加快」

## 背景

G202 已为 catalog `ErrorBody`/`ErrorResponse` 补齐可选 `details`。
Live elevation emit 稳定包含 `details.fields[]`，但 schema 未声明该已知键。

## 决策

1. 全 catalog OpenAPI：在 `details` 下文档化可选 `fields: string[]`
   （仍 `additionalProperties: true`，不排斥其他键）。  
2. Inventory：`milestone=PHX-G204`；
   `t0188_status=mount_parity_complete_error_details_fields_shape_honest`；
   ops **1.0.28**。  
3. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Per-code exhaustive details enum  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G204_ARCHITECTURE_GATE.md](../project/PHX-G204_ARCHITECTURE_GATE.md)  
