# PHX-G197 OpenAPI Ops GatewayDetailError KernelError Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Ops OpenAPI / Inventory  
**规范源：** ADR-0216  
**授权：** DAL-G003 + DAL-G004（DAL-U070）

## 1. 门禁目标

完成最后一处 catalog `KernelError` 扁平信封漂移，对齐 FastAPI detail envelope。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| KernelError | `$ref: GatewayDetailError` |
| ErrorResponse | closed + optional `details` |
| Inventory | PHX-G197 / ops 1.0.23 |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0216 + OpenAPI + inventory + contracts + DAL-U070 + tip/status 齐。  
