# ADR-0211 — OpenAPI Identity/Org/Knowledge Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G192  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U065**；PO cue「充分授权…自主开发…加快」

## 决策

1. Identity OpenAPI **1.0.4** / Organization **1.0.3** / Knowledge **1.0.4**：
   `FoundationStatusData` → emitted field parity（`writable` const false；
   `supported_surfaces` required）。  
2. Inventory：`milestone=PHX-G192`；
   `t0188_status=mount_parity_complete_identity_org_knowledge_status_body_field_parity`。  
3. Ops OpenAPI **1.0.19** 同步。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Full OpenAPI semantic parity  
- HARD HOLD openings  

## 关联

- [../project/PHX-G192_ARCHITECTURE_GATE.md](../project/PHX-G192_ARCHITECTURE_GATE.md)  
