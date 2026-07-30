# PHX-K09 Workflow Kernel Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Core Kernel / Workflow  
**规范源：** BOOK13、BOOK19、BOOK22、BOOK23、ADR-0008、ADR-0024

## 1. 门禁目标

将 Foundation 单级审批切片提升为可声明的审批唯一真相源：定义版本生命周期、批准绑定完整、并发闭合、SLA、升级、补偿最小语义，以及 OpenAPI / 状态机 / 事件目录对等物。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Workflow 唯一拥有审批/路由/任务/升级/补偿真相 |
| Dual gate | Permission.Evaluate →（高影响时）Workflow approval → Commit |
| Binding | principal + action + resource_ref；可选 plan_version/scope/expires_at 一旦出现即强制 |
| Definition | ACTIVE 文档不可变；DEPRECATED 不可 start |
| Concurrency | expected_version CAS；Signal 幂等收敛 |
| SLA | due_at；逾期不得视为批准 |
| Escalation | PENDING_APPROVAL + reason；改派 assignee |
| Compensation | compensating → compensated 显式路径；非 2PC |
| CloseTenant | 需已批准 `organization.tenant.close` 绑定 |
| Events | 目录在 K09；可靠 delivery 归 PHX-P11 |

## 3. Workflow Action / Resource Contract

### 管理 / 运行动作

- `workflow.definition.register`
- `workflow.definition.deprecate`
- `workflow.instance.start`
- `workflow.instance.signal`
- `workflow.instance.cancel`
- `workflow.instance.compensate`
- `workflow.task.approve`
- `workflow.task.reject`
- `workflow.task.escalate`
- `workflow.instance.read`
- `workflow.task.read_all`

### 资源

- `workflow_definition:{definition_id}`
- `workflow_instance:{instance_id}`
- `workflow_task:{task_id}`

## 4. 实现切片

### Slice A — Foundation Security & Concurrency Closure

- reject 使用独立 `reject` 权限动作
- escalate / cancel 状态与 reason 守卫
- Instance/Task `expected_version`
- Signal 并发幂等收敛
- Approve 绑定 `current_task_id`
- escalate/cancel 契约测试

### Slice B — Definition Lifecycle & Approval Binding

- DeprecateDefinition
- plan_version / scope / expires_at 绑定与校验
- business_key 活跃唯一（同租户）
- 扩展 VerifyApprovedAction

### Slice C — SLA & Escalation Hardening

- Task `due_at`
- 逾期查询与 fail-closed
- Escalate 审计完备

### Slice D — Compensation, Contracts & PostgreSQL

- compensate 最小状态机
- OpenAPI 3.1 / 状态机 / 事件目录
- Alembic `0013`（若需新列）
- PostgreSQL 验收与七步自审

## 5. Exit Criteria

1. 双闸门与批准绑定可测。
2. 并发审批/信号不丢更新、不误报冲突。
3. DEPRECATED 定义不可 start。
4. 逾期批准不可 Verify 通过。
5. 升级与取消契约覆盖。
6. 补偿路径可审计且显式。
7. OpenAPI / State Machine / Data Model / Migration / Code 一致。
8. Workflow PostgreSQL 与完整回归通过。

## 6. Explicit Defer

- 完整 PDL / 多图引擎
- 生产 timer worker
- 可靠 outbox（PHX-P11）
- Terminal Approval UX（PHX-T13）
- AI Runtime 编排（PHX-A12）
- CloseTenant 跨 Kernel 清理执行
