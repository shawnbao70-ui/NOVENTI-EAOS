# ADR-0221 — OpenAPI Cross-Domain ErrorBody/ErrorResponse Details Inventory

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G202  
**归属：** OpenAPI Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U075**；PO cue「充分授权…自主开发…加快」

## 背景

Live gateway 通过 `errors.py` / context elevation 发出可选 `details`，
Ops（G197）与 8 个 `ErrorBody` 域已文档化；auth / permission / organization /
workflow / platform 的 `ErrorResponse` 仍缺 `details`。

## 决策

1. 五域 OpenAPI patch bump，并在 `ErrorResponse` 增加可选 `details`
   （`additionalProperties: true`；对标 G197 Ops）。  
2. Inventory：`milestone=PHX-G202`；
   `t0188_status=mount_parity_complete_errorbody_details_inventory_closed`；
   ops **1.0.27**。  
3. 契约扫描：catalog 内 `ErrorBody`/`ErrorResponse` 均含 `details`。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Semantic-complete claim  
- Per-code details shape enum inventory  
- HARD HOLD openings / Board Promote invent  

## 关联

- [../project/PHX-G202_ARCHITECTURE_GATE.md](../project/PHX-G202_ARCHITECTURE_GATE.md)  
