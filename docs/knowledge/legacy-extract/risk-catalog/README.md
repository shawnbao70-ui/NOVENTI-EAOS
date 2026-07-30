# Legacy Knowledge Extract — Risk Catalog

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/risk-catalog/**`  
**Verified:** 2026-07-23

## Scope 与证据强度

本包不是业务功能说明，也不是源码清单；它把 Legacy 中可观察到的跨域结构性风险编成可追踪的风险 ID。重点覆盖：

- 并行事实源、镜像字段和顺序多写；
- `v14_residual` 仍参与运行时后的语义、owner 与迁移风险；
- 权限空洞、GET 直链写操作、仅 UI 确认和对象级越权风险。

证据等级：

- **Confirmed**：活动路由、服务、仓储或 DDL 可直接证实；
- **Strong gap evidence**：跨目录检索未发现预期闭环；
- **Possible / UNKNOWN**：静态仓库无法确认生产数据、挂载结果或部署配置，并列出检索路径。

## Modules

- [双写与并行事实源](dual_write.md)
- [V14 Residual 风险](v14_residual.md)
- [权限空洞](permission_holes.md)
- 汇总见 [INDEX.md](INDEX.md)

## Boundaries

- 只交叉引用既有 [Finance](../finance/) / [Ops](../ops/) / [Governance](../governance/) 知识，不改写这些正文。
- “缓解备注”是 EAOS 迁移约束，不是对 Legacy 开发新 CRUD 的建议。
- 不把旧审计报告中的计划、PASS 或 “extracted” 标签自动等同当前业务语义安全。
