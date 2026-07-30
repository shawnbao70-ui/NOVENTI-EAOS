# ADR-0398 — Controlled Reship Boundary

**状态：** Accepted（PHX-G370）  
**日期：** 2026-07-26  
**里程碑：** PHX-G370  
**授权源：** [Coding Authorization](../project/INV_CONTROLLED_RESHIP_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 受控重发须新发运身份（新幂等键 + 新 posting）。  
2. 禁止复用原 ship 幂等键静默重发。  
3. Unship ≠ 自动授权复用原身份。
