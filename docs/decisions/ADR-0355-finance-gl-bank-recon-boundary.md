# ADR-0355 — Finance GL Bank Reconciliation Boundary

**状态：** Accepted（PHX-G323 / GL5）  
**日期：** 2026-07-26  
**里程碑：** PHX-G323  
**授权源：** [Coding Authorization](../project/FIN_GL_BANK_RECON_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. BankStatement 为租户侧对账壳；行可 match/clear 到 journal line 或 receipt（最小集）。  
2. 无 PSP 实网、无 F3；状态机保持可审计。  
3. RET/AP/Z3/Brain/Twin Out。
