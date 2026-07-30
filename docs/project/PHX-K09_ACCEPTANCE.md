# PHX-K09 Workflow Kernel Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Core Kernel / Workflow  
**退出门禁：** 定义版本 / 审批绑定 / SLA / 升级 / 补偿 + PostgreSQL

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | reject 独立鉴权、escalate/cancel 守卫、expected_version CAS、Signal 幂等收敛 |
| B | DeprecateDefinition、plan_version/scope/expires_at 绑定、business_key 活跃唯一 |
| C | Task due_at、逾期 fail-closed |
| D | compensate 最小状态机、OpenAPI 3.1、状态机、事件目录、Alembic `0013` |

## 2. 核心不变量

- Workflow 是审批/路由/任务/升级/补偿唯一真相源。
- Permission allow 不替代 Workflow approval。
- 批准绑定 principal + action + resource；可选 plan_version/scope/expires_at 一旦出现即强制。
- Instance/Task 更新使用 `expected_version`。
- DEPRECATED 定义不可 start。
- 逾期审批任务不可批准；过期批准不可 Verify。
- Escalate 仅 PENDING_APPROVAL；reason 必填。
- 补偿为显式 `compensating → compensated`，非 2PC。

## 3. 自动化证据

- 本地完整回归：`215 passed`
- 专用 PostgreSQL 17：`12 passed`
- Alembic head：`0013_workflow_k09`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过 |
| Constitution Review | 通过；BOOK13/19/22/23 与 ADR-0008/0024 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过 |
| Gap Analysis | 阻断项关闭；PDL/outbox/Terminal UX 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 完整 PDL / 多图引擎
- 生产 timer worker
- 可靠 outbox（PHX-P11）
- Smart Terminal Approval UX（PHX-T13）
- AI Runtime 编排（PHX-A12）
- CloseTenant 跨 Kernel 清理执行

## 6. 证据索引

- [PHX-K09 Architecture Gate](PHX-K09_ARCHITECTURE_GATE.md)
- [ADR-0024](../decisions/ADR-0024-workflow-approval-truth.md)
- [Workflow Interface](../architecture/WORKFLOW_INTERFACE.md)
- [Workflow State Machines](../architecture/WORKFLOW_STATE_MACHINES.md)
- [Workflow Events](../architecture/WORKFLOW_EVENTS.md)
- [Workflow OpenAPI](../api/workflow.openapi.yaml)
