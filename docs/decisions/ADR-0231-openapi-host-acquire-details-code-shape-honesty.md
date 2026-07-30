# ADR-0231 — OpenAPI Host-Acquire Details Per-Code Shape Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G212  
**归属：** OpenAPI Inventory / Marketplace  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U085**；PO cue「充分授权…自主开发…加快」

## 背景

Tip Next 列出 host-acquire `package_key` details。Live host-acquire
allowlist deny 发出 `COMMON_VALIDATION_FAILED` + `details.package_key`，
但 marketplace OpenAPI 未命名该形状。

## 决策

1. marketplace 新增 `HostAcquireAllowlistDenialDetails`（required `package_key`）。  
2. `ErrorBody.details` 文档化 `package_key` 键（仍 additionalProperties: true）。  
3. marketplace **1.2.8**；Inventory `milestone=PHX-G212`；
   `t0188_status=mount_parity_complete_host_acquire_details_code_shape_honest`；
   ops **1.0.32**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。  
5. 不开放 non-allowlist catalog / arbitrary scripts。

## Explicit Out

- Non-allowlist catalog deepen（需 PO）  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G212_ARCHITECTURE_GATE.md](../project/PHX-G212_ARCHITECTURE_GATE.md)  
