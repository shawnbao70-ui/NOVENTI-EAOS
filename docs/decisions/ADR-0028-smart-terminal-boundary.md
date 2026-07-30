# ADR-0028 — Smart Terminal 边界与交互真相分离

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-T13  
**归属：** Smart Terminal（独立受治理交互层）

## 背景

BOOK23 与 Smart Terminal Blueprint 要求终端呈现意图、预览、权限与审批，但不持有业务真相。PHX-A12 已交付 AI Runtime approval bridge；PHX-T13 需固定实现落点、会话上下文派生与 Commit 闸门。

## 决策

### 1. Ownership 与落点

- Smart Terminal 独立于 Constitutional Kernel、Core Kernel、Platform Runtime、Shared Capability、Business Package 与 Enterprise Brain。
- 技术实现：`smart_terminal/`（Python 可导入包；架构别名 Smart Terminal 层）。
- 不放入 `kernel/`、`runtime/` 或 `eaos_platform/`。

### 2. 信任上下文

- Terminal Session 仅从受信 `ExecutionContext` 派生 Subject / Tenant / Session / Correlation。
- 客户端 `claimed_tenant_id` / `claimed_subject_id` 若与上下文不一致 → `TERMINAL_CONTEXT_ELEVATION_DENIED`。
- 设备不可信时默认拒绝高影响 Commit。

### 3. 交互状态 vs 业务真相

- Terminal 可持久化：会话壳、意图草稿、计划预览快照、批准引用、提交回执（presentation / workspace）。
- Terminal **不得** 成为 Permission、Workflow、Identity、Knowledge 或业务实体的真相源。
- `PresentApproval` 每次从 Workflow 读取当前状态；本地仅缓存 `approval_ref`。

### 4. 命令生命周期

```text
OpenSession → ComposeIntent → BuildPreview
  → RequestApproval（如需）→ PresentApproval
  → Commit（Permission + 可选 Workflow verify）→ Receipt
```

- Preview 与 Commit 分离；变更 action / resource / plan_version / scope 使旧预览失效。
- 高影响 Commit 必须 `Workflow.verify_approved_action`；拒绝/过期/不匹配 → 零提交。

### 5. 与 AI Runtime 的关系

- Agent 工具执行仍经 `runtime/ai`；Terminal 不直接 Invoke 未声明工具。
- 本里程碑 Commit 交付受治理回执，不写入业务包实体。

## Explicit Defer

- 完整 UI Shell / 浏览器客户端
- Extension Host / Marketplace 沙箱
- Accessibility / i18n 产品化矩阵
- Enterprise Brain / Digital Twin 呈现
- FastAPI Router

## 关联

- [ADR-0021-constitutional-platform-layering.md](ADR-0021-constitutional-platform-layering.md)
- [ADR-0024-workflow-approval-truth.md](ADR-0024-workflow-approval-truth.md)
- [ADR-0027-ai-runtime-boundary.md](ADR-0027-ai-runtime-boundary.md)
- [../blueprint/SMART_TERMINAL_BLUEPRINT.md](../blueprint/SMART_TERMINAL_BLUEPRINT.md)
- [../project/PHX-T13_ARCHITECTURE_GATE.md](../project/PHX-T13_ARCHITECTURE_GATE.md)
