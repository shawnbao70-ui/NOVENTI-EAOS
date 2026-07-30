# ADR-0361 — Purchase AP Bill Line Boundary

**状态：** Accepted（PHX-G329 / AP2）  
**日期：** 2026-07-26  
**里程碑：** PHX-G329  
**授权源：** [Coding Authorization](../project/PURCHASE_AP_BILL_LINE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. `ApBillLine` 仅在父账单 `draft` 时可写；amount = qty × unit_price。  
2. 父 `total_amount` = 活动行合计。  
3. 不开 issue/post/pay。
