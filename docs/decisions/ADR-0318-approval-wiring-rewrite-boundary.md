# ADR-0318 — Approval Wiring Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → Kernel Workflow / future Package commands  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；仍不得凭本文件打开 CRUD / 放宽 fail-closed / 改 Identity 实现

## 背景

Legacy 知识抽取表明：Approval Center 具备 Pending→Approved/Rejected 运行时，但 Quote/SO/Convert/Ship **未**调用中央 `create_approval`；V18 Human Confirm（Type A 本地确认）≠ Center Approved；`create_quote_approval` 辅助表 ≠ 中央审批；多步 Workflow 多为 scaffold（`implemented=false`）；Center 批准/拒绝存在 GET 变异与 CSRF 风险。中央审批在商链上为**旁路**，不是运行门禁。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/approval-center-deepen/**`
- `docs/knowledge/legacy-extract/approval-submit-hooks-deepen/**`
- `docs/knowledge/legacy-extract/governance/approval.md`
- `docs/knowledge/legacy-extract/command-authz-deepen/**`（GET 写交叉）
- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) / [ADR-0313](ADR-0313-command-authz-rewrite-boundary.md)

## 决策

1. **Human Confirm（本地 Type A）与中央/多步审批必须分词、分状态、分命令**；禁止将「已确认」标签直接映射为「审批通过」。  
2. **若产品启用中央或 Kernel Workflow 审批**，业务命令（至少可配置于 Quote 发布、Convert、SO 放行、Ship/高影响履约）必须经显式 **submit → 决策消费 → 回调/门禁放行** 挂钩；未挂钩的 Approval Center UI 不得称为已治理商链。  
3. **未启用中央审批时**，本地确认门禁须在 Package/Workflow 策略中显式声明，并仍遵守 [ADR-0313](ADR-0313-command-authz-rewrite-boundary.md)（default-deny、禁 GET 写）。  
4. **多步/并行/条件审批**仅在可执行运行时（非 metadata-only / `implemented=false`）下方可标为可用；scaffold 不得对操作者呈现为已接线。  
5. **批准/拒绝/撤回**必须为非安全方法写命令，带命令身份、主体、对象范围与审计；浏览器 `confirm` 不构成授权。  
6. **审批通过 ≠ 业务副作用自动完成**：Convert/Ship 等仍受 [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) / [ADR-0314](ADR-0314-fulfillment-rewrite-boundary.md) 约束；审批只解除门禁或授权后续命令。  
7. **本 ADR 不打开** Approval Center 产品 CRUD、不自选 Brain execute / Twin authorize、不修改 Constitution Workflow 正文。

## 后果

- Package Surface 设计须先声明「本地确认 / 中央审批 / 二者编排」策略，再画屏。  
- 与命令鉴权 ADR 同时生效：无挂钩的「审批中心」页面权限 ≠ 商链门禁。

## 非目标

- 不定案具体步骤引擎 DSL  
- 不迁移 Legacy `approval_records` 行数据  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0313](ADR-0313-command-authz-rewrite-boundary.md) 命令鉴权  
- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) Approve vs Convert  
- [ADR-0112](ADR-0112-permission-roles-status.md)（只读交叉，若存在）  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
