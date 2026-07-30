# ADR-0387 — Commission Status Deepen Boundary

**状态：** Accepted（PHX-G356）  
**日期：** 2026-07-26  
**里程碑：** PHX-G356  
**授权源：** [Coding Authorization](../project/FIN_COMMISSION_STATUS_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 佣金状态显式流转；Convert 不静默推进。  
2. 非法迁移 fail-closed 且可审计。  
3. 不打开打款 PSP。
