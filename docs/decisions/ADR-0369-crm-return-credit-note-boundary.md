# ADR-0369 — RET → Credit Note Link Boundary

**状态：** Accepted（PHX-G337）  
**日期：** 2026-07-26  
**里程碑：** PHX-G337  
**授权源：** [Coding Authorization](../project/CRM_RETURN_CREDIT_NOTE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Restock 不静默开立 Credit Note；须显式命令且 RMA 已 restocked 并带 invoice_id。  
2. 链接可审计、每 RMA 幂等；Credit Note 先 draft，issue 仍走 Finance 人确权。  
3. 打印/状态标签 alone 不构成冲销。
