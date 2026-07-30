# ADR-0378 — Party Balance Authority Boundary

**状态：** Accepted（PHX-G346）  
**日期：** 2026-07-26  
**里程碑：** PHX-G346  
**授权源：** [Coding Authorization](../project/FIN_PARTY_BALANCE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 主体余额由事件+分配计算；禁止并列两套都称「余额」。  
2. 未分配收款单独披露，不并入已勾兑余额。  
3. Alembic none（只读投影）。
