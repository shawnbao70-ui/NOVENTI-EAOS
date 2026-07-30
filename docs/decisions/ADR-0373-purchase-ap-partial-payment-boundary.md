# ADR-0373 — AP Multi Partial Payment Boundary

**状态：** Accepted（PHX-G341）  
**日期：** 2026-07-26  
**里程碑：** PHX-G341  
**授权源：** [Coding Authorization](../project/PURCHASE_AP_PARTIAL_PAYMENT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 同一 ApBill 允许多次部分 apply；`paid_amount` 为权威已分配合计。  
2. remaining = total − paid；超额 fail-closed。  
3. 付款登记仍 ≠ 清算，直至 apply。
