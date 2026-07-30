# Knowledge Domain Event Catalog

**文档 ID：** EVT-KNOWLEDGE-001  
**版本：** 1.1  
**里程碑：** PHX-K10 specification / PHX-P11 delivery / PHX-E19 wiring  
**命名：** ADR-0006 `domain.entity.action`（ADR-0034 归一）

## Ownership

Knowledge Shared Capability 产生事实；Shared Event Capability 负责持久化、outbox、投递、重试与 DLQ。PHX-K10 不在 Core Kernel 内复制 Event Bus。

## Event Names

| Event | 触发事实 |
|-------|----------|
| `knowledge.entity.upserted` | Entity 创建或更新成功 |
| `knowledge.link.created` | Link 创建成功 |
| `knowledge.entity.archived` | Entity 进入 archived |
| `knowledge.entity.shared` | `shared_with_subject_ids` 扩展 |
| `knowledge.provenance.recorded` | 出处记录追加 |

## Required Envelope

使用 ADR-0006 immutable event envelope，并至少包含：

- `event_id`, `event_name`, `schema_version`
- `tenant_id`, `subject_id`, `correlation_id`
- `occurred_at`, `producer`
- entity/link id、layer、前后 `version`（若适用）
- provenance `source_ref` 摘要（不得含秘密）

不得在 payload 中放置凭证、秘密、完整未授权属性或跨租户标识细节。

## Delivery Gate

PHX-E19 将本目录事件接到同事务 outbox；投递可靠性仍依赖 worker `dispatch_due`，不等同于同步 publish。
