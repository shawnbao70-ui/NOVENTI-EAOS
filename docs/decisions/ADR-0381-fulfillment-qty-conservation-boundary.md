# ADR-0381 — Fulfillment Qty Conservation Boundary

**状态：** Accepted（PHX-G349）  
**日期：** 2026-07-26  
**里程碑：** PHX-G349  
**授权源：** [Coding Authorization](../project/CRM_FULFILLMENT_QTY_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 数量守恒硬门禁；禁止无剩余量控制的重复全量 DO。  
2. SO 履约状态由累计发运证据聚合。  
3. Reopen≠库存冲销（本切片不打开 Unship）。
