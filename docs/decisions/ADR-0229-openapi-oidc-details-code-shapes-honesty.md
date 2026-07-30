# ADR-0229 — OpenAPI OIDC Details Per-Code Shapes Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G210  
**归属：** OpenAPI Inventory / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U083**；PO cue「充分授权…自主开发…加快」

## 背景

Tip Next 列出 other error-code `details` shapes。G208 已闭合 elevation；
live OIDC assert 稳定发出 claim/role/amr/acr details，但 auth OpenAPI
未按码命名。

## 决策

1. auth OpenAPI 新增：  
   - `OidcRequiredClaimMissingDetails`（`claims[]`）  
   - `OidcRoleRequiredDetails`（`role_claim` + `mapped_roles`）  
   - `OidcAmrRequiredDetails` / `OidcAcrRequiredDetails`（+ MFA hint keys）  
2. `ErrorResponse.details` 文档化上述已知键（仍 `additionalProperties: true`）。  
3. auth **1.3.16**；Inventory `milestone=PHX-G210`；
   `t0188_status=mount_parity_complete_oidc_details_code_shapes_honest`；
   ops **1.0.31**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Exhaustive ERROR_CODES details map  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G210_ARCHITECTURE_GATE.md](../project/PHX-G210_ARCHITECTURE_GATE.md)  
