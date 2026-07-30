# ADR-0216 — OpenAPI Ops GatewayDetailError KernelError Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G197  
**归属：** Ops OpenAPI / Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U070**；PO cue「充分授权…自主开发…加快」

## 背景

G166/G174 已将多数域的 `KernelError` 对齐为 FastAPI `{detail:…}` 信封；
Ops 是唯一仍把 `KernelError` 文档为扁平 `ErrorResponse` 的目录契约，
且 `ErrorResponse` 缺少 live elevation `details.fields`。

## 决策

1. Ops OpenAPI **1.0.23**：`KernelError` → `$ref: GatewayDetailError`。  
2. `ErrorResponse`：`additionalProperties: false`；可选 `details`。  
3. Inventory：`milestone=PHX-G197`；
   `t0188_status=mount_parity_complete_ops_gateway_detail_error_parity`。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- HARD HOLD openings  
- Cross-domain ErrorBody.details semantic inventory  

## 关联

- [../project/PHX-G197_ARCHITECTURE_GATE.md](../project/PHX-G197_ARCHITECTURE_GATE.md)  
