# ADR-0400 — Realized FX → GL Bridge Boundary

**状态：** Accepted（PHX-G372）  
**日期：** 2026-07-26  
**里程碑：** PHX-G372  
**授权源：** [Coding Authorization](../project/FIN_REALIZED_FX_GL_BRIDGE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. G359 汇差事件可显式过账；开账期 + 幂等。  
2. 须配置 fx_gain / fx_loss。  
3. 不静默自动过账于 allocation。
