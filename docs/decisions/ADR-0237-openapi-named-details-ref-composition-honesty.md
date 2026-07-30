# ADR-0237 — OpenAPI Named Details $ref Composition Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G218  
**归属：** OpenAPI Inventory / Auth / Marketplace / Ops / Terminal  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U091**；PO cue「充分授权…自主开发…加快」

## 背景

G208–G214 已命名 per-code `*Details` schema，但 `ErrorResponse` /
`ErrorBody.details` 仅用扁平 properties 描述，named schemas 在契约内未被
`$ref` 引用，机器可读组合关系缺失。

## 决策

1. auth `ErrorResponse.details`：`anyOf` → Oidc*Details + residual object。  
2. marketplace `ErrorBody.details`：`anyOf` → HostAcquireAllowlistDenialDetails + residual。  
3. ops / terminal：`anyOf` → ContextElevationDenialDetails + residual。  
4. auth **1.3.18**；marketplace **1.2.9**；terminal **1.1.10**；
   Inventory `milestone=PHX-G218`；
   `t0188_status=mount_parity_complete_named_details_ref_composition_honest`；
   ops **1.0.35**。  
5. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G218_ARCHITECTURE_GATE.md](../project/PHX-G218_ARCHITECTURE_GATE.md)  
