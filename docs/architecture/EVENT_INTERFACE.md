# Event Bus 接口规格

**文档 ID：** IF-EVENT-001  
**版本：** 1.1  
**阶段：** PHX-P11 / PHX-E21  
**状态：** Outbox / Worker / DLQ / Webhook 传输已接受  
**仓库：** `NOVENTI-EAOS`

---

## 目的

定义不可变事件信封、Transactional Outbox、Worker 投递、退避重试、DLQ 与受控重放接口。

## 不变式

1. 信封字段完整且事件名符合 `domain.entity.action`
2. 信封创建后不可修改，payload 深度冻结
3. 发布、入队、订阅、调度、重放均经 Permission Kernel 求值
4. 订阅严格绑定租户，不允许跨租户投递
5. `(subscriber_id, event_id)` 最多成功投递一次
6. `enqueue` 与业务写同事务；`publish` 为同步兼容路径
7. 失败投递按退避重试；超限进入 DLQ
8. DLQ 重放需 `replay` 权限并审计
9. API 不接受客户端声明 `tenant_id` / `session_id` / `platform_scope` / `execution_context`

## 接口

### Event.Subscribe

- **HTTP：** `POST /events/subscriptions`
- 输入：`subscriber_id`、`event_name`（精确名称或 `*`）、可选 `delivery_url`（PHX-E21 webhook）
- 权限：`event_stream:subscribe`
- 输出：`subscription_id`
- 备注：无 `delivery_url` 时 HTTP 面登记 no-op；有 URL 时由 Event Bus 在 `dispatch_due` 路径 POST 信封摘要

### Event.Publish

- **HTTP：** `POST /events`
- 输入：`event_name`、`schema_version`、`producer`、`payload`
- 权限：`event_stream:publish`
- 输出：投递报告（调用内投递；兼容路径）

### Event.Enqueue

- **HTTP：** `POST /events/outbox`
- 输入：同 Publish
- 权限：`event_stream:publish`
- 输出：`outbox_id`（不立即投递）

### Event.DispatchDue

- **HTTP：** `POST /events/dispatch`
- 输入：`worker_id`、`limit?`
- 权限：`event_stream:dispatch`
- 输出：outbox / retry / DLQ 计数

### Event.GetDeliveryStats

- **HTTP：** `GET /events/stats`
- 权限：`event_stream:read`
- 输出：pending/leased outbox、failed deliveries、DLQ depth

### Event.Replay / ListDeadLetters / ReplayDeadLetter

- **HTTP：** `POST /events/{eventId}/replay`、`GET /events/dead-letters`、`POST /events/dead-letters/{id}/replay`
- 权限：`event_stream:replay`

## 错误

- `EVENT_ENVELOPE_INVALID`
- `EVENT_NOT_FOUND`
- `EVENT_SUBSCRIPTION_INVALID`
- `EVENT_DELIVERY_FAILED`
- `EVENT_OUTBOX_NOT_FOUND`
- `EVENT_DEAD_LETTER_NOT_FOUND`
- `EVENT_LEASE_CONFLICT`
- `PERMISSION_DENIED`

## 关联

- [EVENT_STATE_MACHINES.md](EVENT_STATE_MACHINES.md)
- [../api/event.openapi.yaml](../api/event.openapi.yaml)
- [../decisions/ADR-0006-event-envelope.md](../decisions/ADR-0006-event-envelope.md)
- [../decisions/ADR-0011-event-delivery-persistence.md](../decisions/ADR-0011-event-delivery-persistence.md)
- [../decisions/ADR-0026-event-outbox-worker-dlq.md](../decisions/ADR-0026-event-outbox-worker-dlq.md)
- [../project/PHX-P11_ARCHITECTURE_GATE.md](../project/PHX-P11_ARCHITECTURE_GATE.md)
