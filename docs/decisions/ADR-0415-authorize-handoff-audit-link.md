# ADR-0415 — Authorize ↔ Handoff Audit Link

**状态：** Accepted（PHX-G392）  
**日期：** 2026-07-27  
**里程碑：** PHX-G392  

## 决策

1. Commercial handoff ok 记录必须携带 `authorization_audit_id`，指向本次
   Brain execute / Twin authorize 的审计 id。
2. Handoff 自身 `audit_id` 与授权 `authorization_audit_id` 分离，便于关联追踪。
3. 无 Alembic；不改变商业状态机语义。
