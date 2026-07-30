# ADR-0217 — OpenAPI Terminal Extension List Response Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G198  
**归属：** Terminal OpenAPI / Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U071**；PO cue「充分授权…自主开发…加快」

## 背景

`GET /terminal/extensions` 已有稳定 `{data:[…]}` emit（`serialize_extension_list`），
但 OpenAPI 200 缺少 response schema——Tip Next 明确的 list envelope 缺口。

## 决策

1. Terminal OpenAPI **1.1.5**：`TerminalExtensionListEnvelope` + `TerminalExtensionEntry`
   field parity（status enum registered|active|revoked）。  
2. Inventory：`milestone=PHX-G198`；
   `t0188_status=mount_parity_complete_terminal_extension_list_response_parity`；
   ops **1.0.24**。  
3. 不改变 Extension Host sandbox；不执行任意扩展代码。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Arbitrary extension script execution  
- HARD HOLD openings  
- Cross-domain ErrorBody.details inventory  

## 关联

- [../project/PHX-G198_ARCHITECTURE_GATE.md](../project/PHX-G198_ARCHITECTURE_GATE.md)  
