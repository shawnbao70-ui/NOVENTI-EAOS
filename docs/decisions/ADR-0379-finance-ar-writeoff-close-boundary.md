# ADR-0379 — AR Write-off + Close Boundary

**状态：** Accepted（PHX-G347）  
**日期：** 2026-07-26  
**里程碑：** PHX-G347  
**授权源：** [Coding Authorization](../project/FIN_AR_WRITEOFF_CLOSE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 核销/关闭为显式命令；收款≠关闭。  
2. write-off 计入主体余额扣减。  
3. 关闭仅当剩余敞口为零。
