# ADR-0011 — Event 持久化、投递保证与死信策略

**状态：** 已接受  
**日期：** 2026-07-18  
**仓库：** `NOVENTI-EAOS`

---

## 上下文

PHX-004 已实现内存 Event Bus，用于验证信封、权限、租户隔离与幂等。生产级 PHX-P11 需要明确持久化与故障语义。

## 决策

### 1. 持久化

- 生产事件存储采用**追加写（append-only）**
- 已接受事件不可原地修改或删除
- 信封、payload、schema version 与发布时间整体持久化
- 发布与业务状态写入采用 Transactional Outbox 或等价原子方案

### 2. 投递保证

- 采用 **at-least-once** 投递
- 不宣称 exactly-once；业务幂等由 `(subscriber_id, event_id)` 保证
- 订阅者仅在处理成功后确认
- 重试不得改变原始事件信封

### 3. 重试与死信

- 瞬时失败按受控退避策略重试
- 超过最大重试次数进入 Dead Letter Queue（DLQ）
- DLQ 条目保留原事件 ID、订阅者、失败原因、重试次数与时间
- DLQ 重放必须显式 `replay` 权限并写审计

### 4. 租户隔离

- 事件、消费位置、DLQ 与重放操作均绑定 `tenant_id`
- 禁止跨租户消费位置或 DLQ 查询

### 5. Foundation 与生产边界

- 当前 `InMemoryEventRepository` 仅用于契约验证
- PHX-P11 持久化适配器必须保持 `EventBus` 对外契约
- 具体 Broker/数据库产品另立 ADR

## 后果

- 发布吞吐受 outbox relay 能力约束
- 消费者必须幂等
- 运维面需提供 lag、失败率、DLQ 深度与重放审计

## 关联

- [ADR-0006-event-envelope.md](ADR-0006-event-envelope.md)
- [ADR-0007-tenant-isolation.md](ADR-0007-tenant-isolation.md)
- [../architecture/EVENT_INTERFACE.md](../architecture/EVENT_INTERFACE.md)
- [../blueprint/EVENT_BLUEPRINT.md](../blueprint/EVENT_BLUEPRINT.md)
