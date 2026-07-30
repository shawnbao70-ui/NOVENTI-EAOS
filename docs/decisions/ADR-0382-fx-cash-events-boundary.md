# ADR-0382 — FX on Cash Events Boundary

**状态：** Accepted（PHX-G350）  
**日期：** 2026-07-26  
**里程碑：** PHX-G350  
**授权源：** [Coding Authorization](../project/FIN_FX_CASH_EVENTS_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 收款/付款须可携带交易汇率与记账币种金额。  
2. 交易币≠记账币时缺汇率 fail-closed。  
3. 不扩大 live FX NETWORK；期间重估仍属 GL4。
