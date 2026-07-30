# ADR-0395 — Three-Way Match Tolerance Boundary

**状态：** Accepted（PHX-G366）  
**日期：** 2026-07-26  
**里程碑：** PHX-G366  
**授权源：** [Coding Authorization](../project/PURCHASE_3WM_TOLERANCE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 匹配策略至少支持金额容差（绝对/百分比之一）。  
2. 默认零容差 = 精确匹配。  
3. 超容差记 mismatch，不静默视为 matched。
