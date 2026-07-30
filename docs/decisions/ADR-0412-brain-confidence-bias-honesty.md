# ADR-0412 — Brain Confidence / Bias Honesty

**状态：** Accepted（PHX-G389）  
**日期：** 2026-07-27  
**里程碑：** PHX-G389  

## 决策

1. confidence / bias_notes 属于 insight payload 表面；status 诚实声明
   `confidence_drives_execution=false` 与 `commercial_auto_write=false`。
2. 置信度不构成执行或商业写权限。
3. 无 Alembic；tip 保持 `0092_finance_realized_fx_gl_bridge_g372`。
