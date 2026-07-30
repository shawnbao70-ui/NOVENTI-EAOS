# ADR-0371 — Brain Commercial Handoff Boundary

**状态：** Accepted（PHX-G339）  
**日期：** 2026-07-26  
**里程碑：** PHX-G339  
**授权源：** [Coding Authorization](../project/BRAIN_COMMERCIAL_HANDOFF_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. G335 execute/authorize 成功 ≠ 商业写；须另开显式 handoff 命令。  
2. 本切片唯一目标：restocked RMA → draft AR Credit Note（G337 命令）。  
3. Alembic none；审计落既有 audit_events；advisory 仍 `execution_authority: none`。  
4. 不打开 Cap→grant。
