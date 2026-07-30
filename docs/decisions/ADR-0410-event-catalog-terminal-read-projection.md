# ADR-0410 — Event Catalog Terminal Read Projection

**状态：** Accepted（PHX-G386）  
**日期：** 2026-07-27  
**里程碑：** PHX-G386  
**授权源：** [Coding Authorization](../project/EVENT_CATALOG_TERMINAL_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 以 `GET /v1/events/catalog` 提供 EVT-COMMERCIAL-001 只读投影；`writable=false`。
2. Terminal 仅做读投影（admin 按钮），不持有业务真相、不 invent catalog 写路径。
3. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
