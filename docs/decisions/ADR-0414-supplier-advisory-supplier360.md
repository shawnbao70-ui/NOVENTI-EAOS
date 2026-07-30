# ADR-0414 — Supplier Advisory over Supplier360

**状态：** Accepted（PHX-G391）  
**日期：** 2026-07-27  
**里程碑：** PHX-G391  

## 决策

1. Advisory 扩读 Supplier360：`GET /v1/purchase/suppliers/{id}/advisory`。
2. `execution_authority=none`；`commercial_auto_write=false`；复用 Supplier360
   读权，不 invent 商业写。
3. 无 Alembic。
