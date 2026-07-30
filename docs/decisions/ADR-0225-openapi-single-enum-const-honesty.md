# ADR-0225 — OpenAPI Single-Value Enum Const Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G206  
**归属：** OpenAPI Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U079**；PO cue「充分授权…自主开发…加快」

## 背景

Tip Next 列出 list/enum const residual。扫描发现 5 处单值 `enum`
未并列 `const`，与仓库既有 posture schema 风格不一致。

## 决策

1. 为下列字段并列 `const`（保留原 `enum`）：  
   - package `ResolvedAction.source` → `package_manifest`  
   - permission `RoleCatalogStatus.catalog_store` → `process_memory`  
   - permission mint/stub `auto_write_step` → `role_grants`  
   - terminal `ApprovalPresentation.source` → `workflow`  
2. 版本：package **1.0.6**；permission **1.1.12**；terminal **1.1.8**。  
3. Inventory：`milestone=PHX-G206`；
   `t0188_status=mount_parity_complete_single_enum_const_honest`；ops **1.0.29**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Per-code exhaustive ErrorBody.details shapes  
- Multi-value enum collapse  
- HARD HOLD openings  

## 关联

- [../project/PHX-G206_ARCHITECTURE_GATE.md](../project/PHX-G206_ARCHITECTURE_GATE.md)  
