# ADR-0392 — AP Write-off + Close Boundary

**状态：** Accepted（PHX-G362）  
**日期：** 2026-07-26  
**里程碑：** PHX-G362  
**授权源：** [Coding Authorization](../project/PURCHASE_AP_WRITEOFF_CLOSE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. AP 核销/关闭对称 AR；付款≠关闭。  
2. write-off 计入供应商余额扣减。  
3. 关闭仅当剩余敞口为零。
