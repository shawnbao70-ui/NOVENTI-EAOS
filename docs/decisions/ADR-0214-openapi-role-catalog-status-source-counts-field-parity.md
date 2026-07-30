# ADR-0214 — OpenAPI RoleCatalogStatus source_counts Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G195  
**归属：** Permission OpenAPI / Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U068**；PO cue「充分授权…自主开发…加快」

## 背景

G185 已将 `RoleGrantProductPosture` 字段对齐，但 `RoleCatalogStatus.source_counts`
仍为开放整数 map，`catalog_store` 亦未枚举。Tip Next 明确建议该缺口。

## 决策

1. Permission OpenAPI **1.1.8**：新增 `RoleCatalogSourceCounts`
   （`catalog` / `oidc_map` / `grant_map`；`additionalProperties: false`）。  
2. `RoleCatalogStatus.source_counts` → `$ref: RoleCatalogSourceCounts`。  
3. `catalog_store` enum `[process_memory]`（对标 process-local emit）。  
4. Inventory：`milestone=PHX-G195`；
   `t0188_status=mount_parity_complete_role_catalog_status_source_counts_field_parity`；
   ops **1.0.21**。  
5. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Cap→grant invent / Role→grant always-on mint  
- HARD HOLD openings（Brain execute / Twin authorize / external PSP / WebAuthn attestation crypto）  
- Inventory semantic-complete claim  

## 关联

- [../project/PHX-G195_ARCHITECTURE_GATE.md](../project/PHX-G195_ARCHITECTURE_GATE.md)  
- [../project/PHX-G195_ACCEPTANCE.md](../project/PHX-G195_ACCEPTANCE.md)  
