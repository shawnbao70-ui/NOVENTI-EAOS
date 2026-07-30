# ADR-0388 — AR Invoice FX Snapshot Boundary

**状态：** Accepted（PHX-G358）  
**日期：** 2026-07-26  
**里程碑：** PHX-G358  
**授权源：** [Coding Authorization](../project/CRM_AR_INVOICE_FX_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. AR 发票须继承/快照 SO 的交易币、记账币、汇率。  
2. 不得仅有 currency 字段而无 FX 传播。  
3. 跨币清算汇差见 G359。
