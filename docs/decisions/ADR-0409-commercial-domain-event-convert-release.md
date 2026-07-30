# ADR-0409 — Commercial Domain Events: Quote.convert + DO.release

**状态：** Accepted（PHX-G384 / PHX-G385）  
**日期：** 2026-07-27  
**里程碑：** PHX-G384 / PHX-G385  
**授权源：** Batch-A PO AUTH（Event Driven deepen）

## 决策

1. 在 G380 边界之上追加：
   - `convert_quote` → `crm.quote.converted`（`crm.package`）
   - `release_delivery_order` → `crm.delivery_order.released`（`crm.package`）
2. 仅在状态转换成功后入队；幂等重放不重复 emit。
3. 与审计并存；不替代 Permission / Workflow；不静默写 Brain。
4. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
