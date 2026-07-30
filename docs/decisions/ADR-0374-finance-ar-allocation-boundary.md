# ADR-0374 — AR Allocation Engine Shell Boundary

**状态：** Accepted（PHX-G342）  
**日期：** 2026-07-26  
**里程碑：** PHX-G342  
**授权源：** [Coding Authorization](../project/FIN_AR_ALLOCATION_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 收款登记 ≠ 应收清算；清算以 allocation 行为准。  
2. 允许部分/多次分配；未分配余额可查询。  
3. 既有 apply 兼容为单行 allocation 便捷路径。
