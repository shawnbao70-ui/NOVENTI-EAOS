# PHX-G199 OpenAPI Terminal Extension Invoke Response Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Terminal OpenAPI / Inventory  
**规范源：** ADR-0218  
**授权：** DAL-G003 + DAL-G004（DAL-U072）

## 1. 门禁目标

诚实文档化 sandboxed invoke 信封，强调 `executed=false`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Invoke 200 | TerminalExtensionInvokeEnvelope |
| executed | const false |
| Inventory | PHX-G199 / ops 1.0.25 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0218 + OpenAPI + inventory + contracts + DAL-U072 + tip/status 齐。  
