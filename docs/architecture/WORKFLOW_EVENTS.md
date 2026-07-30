# Workflow Domain Event Catalog

**文档 ID：** EVT-WORKFLOW-001  
**版本：** 1.1  
**里程碑：** PHX-K09 specification / PHX-P11 delivery / PHX-E19 wiring  
**命名：** ADR-0006 `domain.entity.action`（ADR-0034 归一）

## Ownership

Workflow 产生事实；Shared Event Capability 负责持久化、outbox、投递、重试与 DLQ。PHX-K09 不在 Core Kernel 内复制 Event Bus。

## Event Names

| Event | 触发事实 |
|-------|----------|
| `workflow.instance.started` | 实例自 Start 进入 running 或 pending_approval |
| `workflow.task.approved` | Task pending → approved 且 Instance → approved |
| `workflow.task.rejected` | Task pending → rejected 且 Instance → rejected |
| `workflow.task.escalated` | Task pending 改派 assignee |
| `workflow.instance.cancelled` | Instance 进入 cancelled |
| `workflow.instance.completed` | Instance 进入 completed |
| `workflow.instance.compensated` | Instance 进入 compensated |

## Required Envelope

使用 ADR-0006 immutable event envelope，并至少包含：

- `event_id`, `event_name`, `schema_version`
- `tenant_id`, `subject_id`, `correlation_id`
- `occurred_at`, `producer`
- 资源 ID、前后 `version`
- 状态转换、approval binding 摘要或 task assignee 变化

不得在 payload 中放置凭证、秘密、完整业务 payload 副本或未经授权的个人数据。

## Delivery Gate

PHX-E19 将本目录事件接到同事务 outbox；投递可靠性仍依赖 worker `dispatch_due`，不等同于同步 publish。
