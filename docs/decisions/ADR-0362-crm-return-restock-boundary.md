# ADR-0362 — CRM Return Restock Boundary

**状态：** Accepted（PHX-G330 / RET2）  
**日期：** 2026-07-26  
**里程碑：** PHX-G330  
**授权源：** [Coding Authorization](../project/CRM_RETURN_RESTOCK_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. RMA `draft → restocked`（不可逆）；全量回补；库存与 RMA 同事务。  
2. 数量 ≤ DO 已发运净额；fail closed。  
3. 不自动贷项、不 PSP 退款、不 WMS 隔离。
