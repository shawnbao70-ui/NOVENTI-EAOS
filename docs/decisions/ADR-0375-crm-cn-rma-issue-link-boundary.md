# ADR-0375 — CN Issue ↔ RMA Link Boundary

**状态：** Accepted（PHX-G343）  
**日期：** 2026-07-26  
**里程碑：** PHX-G343  
**授权源：** [Coding Authorization](../project/CRM_CN_RMA_ISSUE_LINK_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 经 RMA 创建的 CN，issue 时必须保持/校验 RMA 链接与发票谱系。  
2. Restock 不静默 issue；退款/打款不开。  
3. 非 RMA 来源的 CN issue 路径可保留（兼容）。
