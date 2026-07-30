# ADR-0389 — Realized FX on Allocation Boundary

**状态：** Accepted（PHX-G359）  
**日期：** 2026-07-26  
**里程碑：** PHX-G359  
**授权源：** [Coding Authorization](../project/FIN_REALIZED_FX_ALLOCATION_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 跨币分配必须可引用已实现汇差；禁止静默吞掉。  
2. 同币路径无汇差事件。  
3. 本切片以可审计事件为最低交付；总账过账可选。
