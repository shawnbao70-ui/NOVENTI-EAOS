# PHX-G174 OpenAPI Auth/Marketplace/Platform Detail Align Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / OpenAPI  
**规范源：** ADR-0193  
**授权：** DAL-G003 + DAL-G004（DAL-U047）

## 1. 门禁目标

将 auth / platform / marketplace 的 KernelError 合同对齐到 GatewayDetailError 信封。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Auth | KernelError → GatewayDetailError；version 1.3.7 |
| Platform | KernelError → GatewayDetailError；version 1.0.1 |
| Marketplace | KernelError → GatewayDetailError；version 1.2.4 |
| Inventory | PHX-G174；full_openapi_http_complete=false |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0193 + OpenAPI + inventory/ops + tests + DAL-U047 + tip/status 齐。  
