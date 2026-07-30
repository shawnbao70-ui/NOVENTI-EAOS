# ADR-0399 — Treasury Transfer + FX Boundary

**状态：** Accepted（PHX-G371）  
**日期：** 2026-07-26  
**里程碑：** PHX-G371  
**授权源：** [Coding Authorization](../project/FIN_TREASURY_TRANSFER_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 转账为显式现金事件，须可携带交易汇率。  
2. ≠ 银行文件导入 / PSP。  
3. 跨币缺汇率 fail-closed。
