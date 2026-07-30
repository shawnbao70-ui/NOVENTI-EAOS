# PHX-G196 OpenAPI RoleGrant Auto-Write Response/Detail Parity Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Permission OpenAPI / Inventory  
**规范源：** ADR-0215  
**授权：** DAL-G003 + DAL-G004（DAL-U069）

## 1. 门禁目标

诚实文档化 Role→grant auto-write 200/503 emit，不改变 fail-closed 默认。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Mint 200 | RoleGrantAutoWriteMintResponse + RoleGrantMintedGrant |
| Stub 503 | RoleGrantAutoWriteStubDetail closed fields |
| Inventory | PHX-G196 / ops 1.0.22 |
| HARD HOLDS | Cap≠grant；always-on mint closed |
| Package / Alembic | `0.2.1` / `0029` |

## 3. Exit Criteria

ADR-0215 + OpenAPI + inventory/ops + contracts + DAL-U069 + tip/status 齐。  
