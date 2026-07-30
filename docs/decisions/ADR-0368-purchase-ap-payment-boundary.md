# ADR-0368 — AP Payment Shell Boundary

**状态：** Accepted（PHX-G336）  
**日期：** 2026-07-26  
**里程碑：** PHX-G336  
**授权源：** [Coding Authorization](../project/PURCHASE_AP_PAYMENT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 银行/登记付款 ≠ AP 清算：须显式 apply 到 posted/partially_paid ApBill。  
2. ApBill：`draft|posted|partially_paid|paid`；post 与 match 分离（match 仍要求 draft）。  
3. 未分配付款不得将账单标为 paid；幂等；无 GL/PSP 副作用（GL 见 G338）。
