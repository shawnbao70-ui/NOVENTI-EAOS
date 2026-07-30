# ADR-0024 — Workflow 审批唯一真相源与并发边界

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-K09  
**归属：** Core Kernel / Workflow

## 背景

PHX-004 Foundation 已实现单级审批状态机、Signal 幂等与 ADR-0008 主体/动作/资源绑定，但缺少乐观锁、完整批准绑定、SLA、补偿、定义废弃与契约对等物，不足以声明「审批唯一真相源」。

## 决策

### 1. 唯一真相源

- Workflow Kernel 是审批、路由、任务、升级与补偿的唯一流程真相源。
- 业务包、Smart Terminal、AI Runtime 不得维护平行审批状态。
- Permission allow 与 Workflow approval 是独立双闸门；allow 永不替代 approval。

### 2. 批准绑定

AI / 高影响批准最少绑定：

- `principal_subject_id`
- `action`
- `resource_ref`
- `plan_version`（可选但一经提供即强制匹配）
- `scope`（可选但一经提供即强制匹配）
- `expires_at`（可选；到期后批准失效）

任一绑定字段变更后，原 `approval_ref` 不可复用。

### 3. 定义版本

- `(tenant|platform, name, version)` 唯一。
- 已发布 ACTIVE 定义文档引用不可变；废弃走 `DEPRECATED`，不可再 start。
- Foundation 管理员 bootstrap 仅用于建立首条治理路径。

### 4. 并发与幂等

- Instance / Task 更新必须提供 `expected_version`；冲突返回 `WORKFLOW_VERSION_CONFLICT`。
- Signal 保持强制幂等键；同键同指纹重放成功；同键不同指纹冲突。
- 并发插入同键同指纹时，败方应收敛为幂等成功而非误报冲突。

### 5. SLA 与升级

- 审批任务可携带 `due_at`。
- 逾期默认 fail-closed：不得视为已批准；可显式 escalate 或取消。
- Escalate 仅在 `PENDING_APPROVAL` 且 task `PENDING` 时允许；reason 必填。

### 6. 补偿最小语义

- 补偿是显式命令，不自动 2PC。
- 仅终态可补偿路径允许的实例可进入 `compensating → compensated`。
- 补偿不撤销 Permission Grant；不自动回滚跨 Kernel 副作用（协调归后续里程碑）。

### 7. 事件

- K09 定义 Workflow 事件目录。
- 可靠 outbox / delivery 归 PHX-P11。

### 8. CloseTenant 审批契约

- Organization `CloseTenant` 执行前必须存在已批准的 Workflow 实例，绑定动作 `organization.tenant.close` 与对应 tenant 资源。
- 清理编排可跨 Kernel；审批契约由本 ADR 固定。

## Explicit Defer

- 完整 PDL 解释器与多图编排引擎
- 生产级 timer worker 集群
- 可靠 event outbox（PHX-P11）
- Smart Terminal Approval UX（PHX-T13）
- AI Runtime 劳动力编排完整实现（PHX-A12）
- CloseTenant 跨 Kernel 清理执行器

## 关联

- [ADR-0008-ai-human-approval.md](ADR-0008-ai-human-approval.md)
- [ADR-0023-permission-policy-scope-delegation.md](ADR-0023-permission-policy-scope-delegation.md)
- [../architecture/WORKFLOW_INTERFACE.md](../architecture/WORKFLOW_INTERFACE.md)
- [../project/PHX-K09_ARCHITECTURE_GATE.md](../project/PHX-K09_ARCHITECTURE_GATE.md)
