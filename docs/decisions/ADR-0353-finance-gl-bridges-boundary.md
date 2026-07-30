# ADR-0353 — Finance GL Bridges Boundary

**状态：** Accepted（PHX-G321 / GL3）  
**日期：** 2026-07-26  
**里程碑：** PHX-G321  
**授权源：** [Coding Authorization](../project/FIN_GL_BRIDGES_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. Bridge 将既有 Finance 事实（AR issue / Receipt apply / Tax issue / Commission accrue）投影为 JournalEntry，幂等键绑定 source 类型+id。  
2. 必须绑定开放 GlPeriod；closed period fail closed。  
3. 科目映射为租户级最小 bridge map（account roles），非 Kernel。  
4. GL4/GL5、Brain/Twin、AP/RET Out。
