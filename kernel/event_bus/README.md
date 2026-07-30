# kernel/event_bus/

Event Bus（PHX-004 foundation + PHX-P11 outbox/DLQ）。

## 已实现

- ADR-0006 不可变事件信封
- Permission 控制的 Publish / Enqueue / Subscribe / Dispatch / Read / Replay
- Transactional Outbox（`enqueue` + `dispatch_due` lease）
- 失败投递指数退避与 DLQ（`replay_dead_letter`）
- 投递观测（`get_delivery_stats`）
- `(subscriber_id, event_id)` 幂等投递
- SQLAlchemy 持久化 + Alembic `0006` / `0015` / `0021`（webhook `delivery_url`）
- TransactionalEventBus 事务接线
- PHX-E21 可选 webhook 传输（SSRF 基础门禁；签名延后）

## 边界

- `publish` 仍为同步兼容路径；可靠路径使用 `enqueue` + worker `dispatch_due`
- 规范归属 Shared Platform Capability；本目录为兼容物理路径
- Webhook HMAC 签名、外部 Broker、多区域韧性显式延后

## 测试

```bash
python -m pytest tests/contracts/test_event_bus.py tests/contracts/test_event_p11.py tests/contracts/test_event_webhook_e21.py -p no:cacheprovider
```

## 规格

- [../../docs/architecture/EVENT_INTERFACE.md](../../docs/architecture/EVENT_INTERFACE.md)
- [../../docs/decisions/ADR-0026-event-outbox-worker-dlq.md](../../docs/decisions/ADR-0026-event-outbox-worker-dlq.md)
- [../../docs/decisions/ADR-0051-event-webhook-transport.md](../../docs/decisions/ADR-0051-event-webhook-transport.md)
