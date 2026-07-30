# ADR-0413 — SO.confirm Commercial Handoff Boundary

**状态：** Accepted（PHX-G390）  
**日期：** 2026-07-27  
**里程碑：** PHX-G390  

## 决策

1. Handoff #2 唯一目标为 SO.confirm；批准（Brain execute / Twin authorize）
   **不等于** 自动 `confirm_sales_order`。
2. 编排仅入队授权审计并返回 `approval_ref`；商业状态转换仍需后续人工 confirm
   （及既有 Workflow 门）。
3. 无 Alembic；无静默 Brain 商业写；Z3 `execution_authority=none`。
