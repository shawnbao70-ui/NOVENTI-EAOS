# ADR-0218 — OpenAPI Terminal Extension Invoke Response Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G199  
**归属：** Terminal OpenAPI / Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U072**；PO cue「充分授权…自主开发…加快」

## 背景

`POST /terminal/extensions/{id}/actions` 返回稳定的 declaration-only invoke 信封
（`executed=false`），但 OpenAPI 200 缺少 schema。

## 决策

1. Terminal OpenAPI **1.1.6**：`TerminalExtensionInvokeEnvelope` +
   `TerminalExtensionInvokeData`（`status` const `accepted_sandboxed`；
   `executed` const `false`）。  
2. Inventory：`milestone=PHX-G199`；
   `t0188_status=mount_parity_complete_terminal_extension_invoke_response_parity`；
   ops **1.0.25**。  
3. 不打开任意扩展执行。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Arbitrary extension script execution  
- HARD HOLD openings  

## 关联

- [../project/PHX-G199_ARCHITECTURE_GATE.md](../project/PHX-G199_ARCHITECTURE_GATE.md)  
