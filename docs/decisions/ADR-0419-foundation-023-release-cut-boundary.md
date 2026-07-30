# ADR-0419 — Foundation 0.2.3 Release Cut Boundary

**状态：** Accepted（PHX-G404）  
**日期：** 2026-07-27  
**里程碑：** PHX-G404  
**授权源：** [Coding Authorization](../project/FOUNDATION_023_RELEASE_CODING_AUTHORIZATION_SUMMARY.md)

## 决策

1. 包版本切至 `0.2.3`；Alembic tip 仍为 `0092_finance_realized_fx_gl_bridge_g372`。  
2. 无业务 CRUD；无新 Alembic revision。  
3. Marketplace 外部 PSP / `ENABLE_*_NETWORK` 仍默认 OFF；银行文件导入仍暂缓。  
4. 本切携带 Batch-D economy shells（G400–G402）与 Workflow multi-step narrow deepen（G403）。
