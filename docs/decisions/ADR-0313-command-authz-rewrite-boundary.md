# ADR-0313 — Command Authorization Rewrite Boundary

**状态：** Accepted（边界决策；非产品实现授权）  
**日期：** 2026-07-23  
**里程碑：** 未分配（产品切片须另开 Gate；本 ADR 不自开 PHX-G）  
**归属：** Knowledge Driven → Kernel Permission / Workflow / future Package commands  
**授权：** DAL-G003 / DAL-G004（CA Accept 重写边界）；Foundation 可对齐本边界加固；仍不得凭本文件打开业务 CRUD / 放宽 fail-closed / 改 Identity 实现

## 背景

Legacy 知识抽取表明：鉴权多为路由 opt-in；模块权限 ≠ 对象/租户范围；大量 **GET 写操作**（含 DO Complete/Reopen、Approval Center approve/reject、PO Receive 等）；Admin/Super Admin 角色串短路通常 **不是** 可审计 override；UI 可见性与服务端授权分离。MASTER_PLAN 与 BOOK 工程顺序要求实现前先固定边界。

主要证据包（只读）：

- `docs/knowledge/legacy-extract/command-authz-deepen/**`
- `docs/knowledge/legacy-extract/permission-surface-deepen/**`
- `docs/knowledge/legacy-extract/approval-submit-hooks-deepen/**`
- `docs/knowledge/legacy-extract/risk-catalog/permission_holes.md`
- Research：`AUTHZ_EXCEPTION_CARD` / `APPROVAL_BOUNDARY_CARD`（仍 0 Complete）

## 决策

1. **EAOS 命令授权默认拒绝（default-deny）。** 未显式授权的写命令不得执行；禁止「有 checker 就当已覆盖」。  
2. **授权维度最低集合**（实现须可评估）：主体（principal）· 权限/动作 · **对象所有权** · **租户范围** · 资源状态 · 高影响意图（preview/approval）· 幂等/命令身份 · 审计。模块菜单可见性不构成授权。  
3. **禁止 GET 变异作为产品命令面。** 状态推进、批准/拒绝、收货、完成/重开等写意图必须使用非安全方法（如 POST）并纳入 CSRF/同等防护；浏览器 `confirm` 不得充当授权。  
4. **特权绕过必须是显式、有范围、可审计的 override 命令**（理由/批准人/时效/对象范围），不得等同于角色名短路。  
5. **Approval Center 与业务 Type A 门禁不得混为一谈。** Legacy 中央审批未挂钩 Quote/SO/Convert/Ship；EAOS 若采用中央审批，必须经 Workflow/命令挂钩显式提交与消费；本地确认门禁须单独建模。  
6. **Cap≠Permission≠Grant** 保持宪章边界；本 ADR 不打开 Role→grant invent、Brain execute、Twin authorize。  
7. **本 ADR 不打开** 业务 CRUD、不修改 Constitution/Blueprint 正文、不放宽现有 fail-closed。

## 后果

- Package Surface / Operator Commit 路径须按命令评估授权，而非按页面。  
- 现有 Smart Terminal 治理探针与演示移交继续受 Foundation 权限模型约束；本提案不扩大 demo 写权限。  
- 后续 Permission/Workflow 深化以实现本边界为准，另开编号切片。

## 非目标

- 不规定具体 RBAC/ABAC 引擎选型细节  
- 不枚举全部 Legacy GET 写清单的迁移脚本  
- 不分配产品 PHX-G；业务 CRUD 须另开 Gate（本 ADR 仅为重写边界）

## 关联

- [ADR-0112](ADR-0112-permission-roles-status.md) 及后续 Permission 产品姿态 ADR（只读交叉）  
- [ADR-0312](ADR-0312-quote-convert-rewrite-boundary.md) Convert 重写边界（Accepted）  
- [legacy-extract README](../knowledge/legacy-extract/README.md)  
- Gap review canvas: `legacy-extract-gap-review`
