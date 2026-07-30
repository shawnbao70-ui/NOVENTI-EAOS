# ADR-0411 — Twin Sync Thin Status Honesty

**状态：** Accepted（PHX-G388）  
**日期：** 2026-07-27  
**里程碑：** PHX-G388  

## 决策

1. Twin 不声明常驻 continuous sync daemon；同步面为 `snapshot_upsert`。
2. `GET /v1/twin/status` 以 closed schema 暴露该姿态；`commercial_auto_write=false`。
3. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
