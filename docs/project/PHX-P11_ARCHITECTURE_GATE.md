# PHX-P11 Event Delivery / Outbox Architecture Gate

**日期：** 2026-07-18  
**状态：** Accepted for Implementation  
**归属：** Shared Platform Capability / Event Bus  
**规范源：** BOOK19、BOOK22、ADR-0006、ADR-0011、ADR-0026  
**退出门禁：** 可恢复、可观测、可重放

## 1. 门禁目标

交付可靠事件投递最小垂直切片：Transactional Outbox、Worker Lease、退避重试、DLQ、投递观测，并保持 `EventBus` 契约兼容。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | Shared Platform Capability；兼容路径 `kernel/event_bus` |
| Outbox | `enqueue` 同事务写入；relay 后发布 |
| Sync publish | 保留兼容；不等同可靠 outbox |
| Lease | `leased_until` / `leased_by`；过期可回收 |
| Retry | 指数退避；超限进 DLQ |
| DLQ | 保留 event/subscriber/reason/attempts；重放需 replay 权限 |
| Observability | pending/leased/failed/DLQ depth 查询 |
| Broker | 本里程碑不引入外部消息中间件 |

## 3. Action / Resource Contract

- `event_stream:publish` — Publish / Enqueue
- `event_stream:subscribe` — Subscribe
- `event_stream:read` — GetEvent / DeliveryStats
- `event_stream:replay` — Replay / ListDLQ / ReplayDLQ
- `event_stream:dispatch` — Worker `dispatch_due`

资源：`event_stream`（租户级）

## 4. 实现切片

### Slice A — Outbox + Enqueue

- Outbox 模型与仓储
- `EventBus.enqueue`（不调用内投递）
- 预分配 `event_id`

### Slice B — Worker Lease + Retry + DLQ

- `dispatch_due` 领取 outbox 并投递
- 失败投递退避重试
- 超限写入 DLQ；`replay_dead_letter`

### Slice C — Persistence

- Alembic `0015_event_outbox_dlq`
- SQLAlchemy + TransactionalEventBus 扩展

### Slice D — Contracts

- OpenAPI / 状态机 / 接口更新
- PostgreSQL 与七步自审

## 5. Exit Criteria

1. 业务意图可经 outbox 原子落库，崩溃后可恢复 relay。  
2. 投递失败可退避重试；超限进入 DLQ。  
3. DLQ 重放需显式权限并审计。  
4. Stats 可观察 pending / failed / DLQ depth。  
5. OpenAPI / Data Model / Migration / Code 一致。  
6. PostgreSQL 与完整回归通过。  
7. 不宣称外部 Broker 或多区域韧性已交付。

## 6. Explicit Defer

- 外部 Broker 与多区域 failover
- K07–K10 领域事件目录全量自动发布接线
- 包路径迁移至 `eaos_platform.event`
- 运维 UI / 外部 metrics 后端
