# ADR-0407 — Outbox Worker / Lease Status Honesty

**状态：** Accepted（PHX-G382）  
**日期：** 2026-07-27  
**里程碑：** PHX-G382  
**授权源：** [Coding Authorization](../project/OUTBOX_WORKER_LEASE_STATUS_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Event Bus 不声明常驻 background worker daemon；投递由 `POST /events/dispatch`
   按需触发，outbox 采用 claim lease（默认 `DEFAULT_LEASE_SECONDS=30`）。
2. `GET /v1/events/status` 以 closed schema 暴露上述诚实字段；不 invent 守护进程
   启停 API。
3. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
