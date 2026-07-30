# ADR-0383 — Convert Terms + FX Snapshot Boundary

**状态：** Accepted（PHX-G352）  
**日期：** 2026-07-26  
**里程碑：** PHX-G352  
**授权源：** [Coding Authorization](../project/CRM_CONVERT_FX_SNAPSHOT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Convert 必须把交易币/记账币/汇率快照写入 SO；省略视为缺陷。  
2. 跨币缺汇率 fail-closed。  
3. 不打开审批挂钩（G353）与佣金流转（G356）。
