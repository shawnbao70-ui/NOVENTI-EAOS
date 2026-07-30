# ADR-0406 — Commercial Domain-Event Honesty Boundary

**状态：** Accepted（PHX-G380）  
**日期：** 2026-07-26  
**里程碑：** PHX-G380  
**授权源：** [Coding Authorization](../project/COMMERCIAL_DOMAIN_EVENT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 本切片仅钉死：`SO.confirm` → `crm.sales_order.confirmed`；`DO.ship` → `inventory.delivery_order.shipped`。  
2. 与审计并存；事件不替代 Permission/Workflow。  
3. 优先复用既有 outbox；无 Alembic 除非确需。
