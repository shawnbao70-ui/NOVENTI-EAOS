# ADR-0386 — Controlled Unship Boundary

**状态：** Accepted（PHX-G355）  
**日期：** 2026-07-26  
**里程碑：** PHX-G355  
**授权源：** [Coding Authorization](../project/INV_CONTROLLED_UNSHIP_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Unship 为独立命令：冲库存 + 恢复履约剩余量。  
2. Unship ≠ Reopen ≠ RMA。  
3. 须人确权、幂等、可审计。
