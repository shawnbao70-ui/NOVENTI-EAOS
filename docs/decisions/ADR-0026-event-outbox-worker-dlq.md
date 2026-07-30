# ADR-0026 — Event Outbox、Worker Lease 与 DLQ

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-P11  
**归属：** Shared Platform Capability / Event Bus

## 背景

ADR-0011 已裁决 Transactional Outbox、at-least-once、退避重试与 DLQ。PHX-004 仅交付调用内投递。PHX-P11 需要固定可恢复、可观测、可重放的最小生产投递切片，同时保持 `EventBus` 对外契约兼容。

## 决策

### 1. Ownership

- Event Bus 规范归属 Shared Platform Capability。
- 本里程碑继续使用兼容路径 `kernel/event_bus/`；完整包迁移显式延后。
- 不引入外部 Broker；产品选型另立 ADR。

### 2. Transactional Outbox

- 新增 `event_outbox`：业务意图与事件信封字段同事务写入。
- `EventBus.enqueue` 仅写 outbox，不在调用内投递。
- `EventBus.publish` 保留为同步兼容路径（Foundation / 测试）。
- Outbox 预分配 `event_id`，relay 幂等：已存在则跳过写入再投递。

### 3. Worker / Lease

- `dispatch_due` 领取 `available_at <= now` 且租约过期/空闲的 pending 行。
- 领取后置 `leased` + `leased_until` + `leased_by`。
- 成功 → `dispatched`；失败按退避更新 `available_at`；超限 → outbox `dead`（毒消息）。
- PostgreSQL 使用行锁领取；SQLite/内存使用等价条件更新。

### 4. Delivery Retry 与 DLQ

- 订阅投递失败保留在 `event_deliveries`（status=`failed`）。
- Worker 对失败投递按指数退避重试。
- 超过 `max_delivery_attempts` → 写入 `event_dead_letters`，delivery 置 `dead`。
- DLQ 重放要求 `event_stream:replay` 并审计。

### 5. 可观测性

- `get_delivery_stats` 暴露：pending/leased outbox、failed deliveries、DLQ depth。
- 不引入外部 metrics 后端；本里程碑以查询接口为观测门禁。

### 6. 权限

| 动作 | resource | action |
|------|----------|--------|
| Enqueue | event_stream | publish |
| Dispatch (worker) | event_stream | dispatch |
| Stats | event_stream | read |
| List/Replay DLQ | event_stream | replay |

## Explicit Defer

- 外部 Broker / 多区域韧性
- K07–K10 全量领域事件自动接线
- `kernel/event_bus` → `eaos_platform.event` 路径迁移
- 跨进程 handler 热恢复编排与运维 UI

## 关联

- [ADR-0011-event-delivery-persistence.md](ADR-0011-event-delivery-persistence.md)
- [ADR-0006-event-envelope.md](ADR-0006-event-envelope.md)
- [../project/PHX-P11_ARCHITECTURE_GATE.md](../project/PHX-P11_ARCHITECTURE_GATE.md)
