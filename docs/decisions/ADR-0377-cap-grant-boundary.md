# ADR-0377 — Cap→grant Narrow Shell Boundary

**状态：** Accepted（PHX-G345）  
**日期：** 2026-07-26  
**里程碑：** PHX-G345  
**授权源：** [Coding Authorization](../project/CAP_GRANT_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Cap→grant 为显式、可审计的 Permission grant 命令壳；default-deny 不变。  
2. 不因 grant 自动执行商业写；不绕过 G339 handoff。  
3. 禁止跨租户与 Legacy Admin bypass。  
4. Alembic 优先 none。
