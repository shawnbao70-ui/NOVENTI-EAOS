# ADR-0360 — Finance Tax Authority Live Network Boundary

**状态：** Accepted（PHX-G328 / Tax-NET）  
**日期：** 2026-07-26  
**里程碑：** PHX-G328  
**归属：** Business Package / Finance  
**授权源：** [Coding Authorization](../project/FIN_TAX_NETWORK_LIVE_CODING_AUTHORIZATION_SUMMARY.md)

## 背景

Tax3 仅交付 network stub（flag ON 仍无 I/O）。PO 授权打开 **live tax** 传输能力：在显式 env 门闩与 endpoint 配置齐全时允许出站 HTTP 校验，默认仍 OFF。

## 决策

1. Flag：`EAOS_TAX_NETWORK` / `ENABLE_TAX_NETWORK`（默认 false）。  
2. Endpoint：`EAOS_TAX_AUTHORITY_URL` 必填才启用 live transport；缺省 → fail-closed stub 行为。  
3. Optional bearer：`EAOS_TAX_AUTHORITY_BEARER`；不得写入日志/审计敏感值。  
4. `live_transport=true` 仅当 flag ON 且 URL 已配置。  
5. 不得通过 API 打开网络；PSP `ENABLE_PSP_NETWORK` 本切片 **Out**。  
6. 无 Alembic。

## 关联

- [ADR-0350](ADR-0350-finance-tax-authority-adapter.md)  
- [Coding Authorization](../project/FIN_TAX_NETWORK_LIVE_CODING_AUTHORIZATION_SUMMARY.md)
