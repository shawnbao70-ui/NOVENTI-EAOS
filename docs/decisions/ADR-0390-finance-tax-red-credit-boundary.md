# ADR-0390 — Tax Void + Red-Credit Boundary

**状态：** Accepted（PHX-G360）  
**日期：** 2026-07-26  
**里程碑：** PHX-G360  
**授权源：** [Coding Authorization](../project/FIN_TAX_VOID_RED_CREDIT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 作废与红冲均为可审计命令；打印 alone 不构成冲销。  
2. 红冲须挂钩原已开立税票。  
3. 不扩大 live tax NETWORK。
