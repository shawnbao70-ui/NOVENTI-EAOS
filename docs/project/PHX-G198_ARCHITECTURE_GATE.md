# PHX-G198 OpenAPI Terminal Extension List Response Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Terminal OpenAPI / Inventory  
**规范源：** ADR-0217  
**授权：** DAL-G003 + DAL-G004（DAL-U071）

## 1. 门禁目标

诚实文档化 Extension list envelope，零运行时行为变更。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| List 200 | TerminalExtensionListEnvelope |
| Entry | TerminalExtensionEntry field parity |
| Inventory | PHX-G198 / ops 1.0.24 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0217 + OpenAPI + inventory + contracts + DAL-U071 + tip/status 齐。  
