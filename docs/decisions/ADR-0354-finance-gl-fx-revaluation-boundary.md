# ADR-0354 — Finance GL FX Revaluation Boundary

**状态：** Accepted（PHX-G322 / GL4）  
**日期：** 2026-07-26  
**里程碑：** PHX-G322  
**授权源：** [Coding Authorization](../project/FIN_GL_FX_REVALUATION_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. FX 重估是期间内命令，产出平衡 JournalEntry；绑开放 GlPeriod。  
2. FxRatePort 默认 RejectAll；Fake 仅测；禁止实网牌价。  
3. GL5、Brain/Twin Out。
