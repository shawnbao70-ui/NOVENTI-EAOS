# Permission Domain Event Catalog

**文档 ID：** EVT-PERMISSION-001  
**版本：** 1.2  
**里程碑：** PHX-K08 specification / PHX-P11 delivery / PHX-E19 wiring / PHX-E20 DecisionRecorded  
**命名：** ADR-0006 `domain.entity.action`（ADR-0034 归一；ADR-0050 接线）

## Ownership

Permission 产生事实；Shared Event Capability 负责持久化、outbox、投递、重试与 DLQ。PHX-K08 不在 Core Kernel 内复制 Event Bus。

## Event Names

| Event | 触发事实 |
|-------|----------|
| `permission.policy.activated` | Policy draft → active |
| `permission.policy.deprecated` | Policy active → deprecated |
| `permission.grant.created` | Direct grant active 创建 |
| `permission.grant.revoked` | Grant active → revoked |
| `permission.grant.delegated` | 自有效父 Grant 创建 delegated grant |
| `permission.decision.recorded` | Evaluate 持久化 decision 与 evidence 摘要（PHX-E20 已接线） |

## Required Envelope

使用 ADR-0006 immutable event envelope，并至少包含：

- `event_id`, `event_name`, `schema_version`
- `tenant_id`, `subject_id`, `correlation_id`
- `occurred_at`, `producer`
- 资源 ID、前后 `version`
- 状态转换、scope 或 matched reference 摘要

不得在 payload 中放置凭证、秘密、策略原文、未经授权的个人数据或完整业务真相副本。

## Delivery Gate

PHX-E19 将状态变更类事件接到同事务 outbox；PHX-E20 接线 `permission.decision.recorded`（高基数，摘要 payload）。投递可靠性仍依赖 worker `dispatch_due`，不等同于同步 publish。
