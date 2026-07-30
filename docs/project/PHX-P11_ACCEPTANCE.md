# PHX-P11 Event Delivery / Outbox Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Shared Platform Capability / Event Bus  
**退出门禁：** 可恢复、可观测、可重放

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | `enqueue` Transactional Outbox；预分配 `event_id` |
| B | `dispatch_due` lease/claim、退避重试、DLQ、`replay_dead_letter` |
| C | Alembic `0015_event_outbox_dlq`、TransactionalEventBus 扩展 |
| D | OpenAPI 3.1、状态机、观测 stats、PostgreSQL 与七步自审 |

## 2. 核心不变量

- Outbox 与业务写可同事务；enqueue ≠ 立即投递。
- Worker 租约可回收；relay 对 `event_id` 幂等。
- at-least-once；`(subscriber_id, event_id)` 成功至多一次。
- 超限进入 DLQ；重放需 `replay` 权限并审计。
- Stats 暴露 pending/leased/failed/DLQ depth。
- `publish` 同步路径保留兼容，不宣称替代 outbox。

## 3. 自动化证据

- 本地完整回归：`240 passed`
- 专用 PostgreSQL 17：`14 passed`
- Alembic head：`0015_event_outbox_dlq`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0011/0026 落地 |
| Constitution Review | 通过；BOOK19/22 不可变事件与受控回放 |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；OpenAPI / Data Model / Migration / Code 一致 |
| Gap Analysis | 阻断项关闭；Broker/多区域/全量领域接线显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 外部 Broker 与多区域韧性
- K07–K10 领域事件目录全量自动发布接线
- `kernel/event_bus` → `eaos_platform.event` 路径迁移
- 运维 UI / 外部 metrics 后端

## 6. 证据索引

- [PHX-P11 Architecture Gate](PHX-P11_ARCHITECTURE_GATE.md)
- [ADR-0026](../decisions/ADR-0026-event-outbox-worker-dlq.md)
- [Event Interface](../architecture/EVENT_INTERFACE.md)
- [Event State Machines](../architecture/EVENT_STATE_MACHINES.md)
- [Event OpenAPI](../api/event.openapi.yaml)
