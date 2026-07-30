# Organization Domain Event Catalog

**文档 ID：** EVT-ORG-001  
**版本：** 1.1  
**里程碑：** PHX-K07 specification / PHX-P11 delivery / PHX-E19 wiring

## Ownership

Organization 产生事实；Shared Event Capability 负责持久化、outbox、投递、重试与 DLQ。PHX-K07 不在 Core Kernel 内复制 Event Bus。

## Event Names

| Event | 触发事实 |
|-------|----------|
| `organization.tenant.created` | Tenant 与 primary Enterprise 原子创建 |
| `organization.tenant.suspended` | Tenant active → suspended |
| `organization.tenant.reactivated` | Tenant suspended → active |
| `organization.enterprise.created` | Enterprise 创建 |
| `organization.unit.created` | Unit 创建 |
| `organization.unit.updated` | Unit 名称、类型、parent 或状态更新 |
| `organization.membership.added` | active Membership 创建 |
| `organization.membership.suspended` | Membership active → suspended |
| `organization.membership.reactivated` | Membership suspended → active |
| `organization.membership.transferred` | active Membership 同 Enterprise 转移 Unit |
| `organization.membership.ended` | Membership → ended |

## Required Envelope

使用 ADR-0006 immutable event envelope，并至少包含：

- `event_id`, `event_name`, `schema_version`
- `tenant_id`, `subject_id`, `correlation_id`
- `occurred_at`, `producer`
- 资源 ID、前后 `version`
- 状态转换或 parent / unit 变化

不得在 payload 中放置凭证、秘密、未经授权的个人数据或完整业务真相副本。

## Delivery Gate

PHX-E19 将本目录事件接到同事务 outbox；投递可靠性仍依赖 worker `dispatch_due`，不等同于同步 publish。
