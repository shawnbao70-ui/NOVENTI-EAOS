# ADR-0366 — Three-Way Match Shell Boundary

**状态：** Accepted（PHX-G334 / AP5）  
**日期：** 2026-07-26  
**里程碑：** PHX-G334  
**授权源：** [Coding Authorization](../project/PURCHASE_THREE_WAY_MATCH_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Match 绑定 PO + 其 GRN + draft ApBill（含行）；同供应商谱系。  
2. `matched|mismatch`；每租户每 PO 唯一；幂等。  
3. 无付款/GL/PSP 副作用。
