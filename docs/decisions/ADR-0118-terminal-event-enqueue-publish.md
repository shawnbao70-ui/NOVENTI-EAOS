# ADR-0118 — Terminal Event Enqueue/Publish Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G99  
**归属：** Smart Terminal / Event Bus

## 背景

G97/G98 已提供 stats/DLQ/dispatch/get 薄探针。运维仍缺 Terminal 内 enqueue（outbox）与同步 publish 的薄调用面。

## 决策

1. Terminal Admin 增加 Enqueue outbox 与 Publish event 薄控件。  
2. 仅调用既有 `POST /v1/events/outbox` 与 `POST /v1/events`。  
3. Body 仅事件字段（name/schema/producer/payload）；禁止 tenant/subject 提升。  
4. 不新增订阅/Webhook 配置 UI；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0116-terminal-event-bus-stats.md](ADR-0116-terminal-event-bus-stats.md)
- [ADR-0117-terminal-event-dispatch.md](ADR-0117-terminal-event-dispatch.md)
- [../project/PHX-G99_ARCHITECTURE_GATE.md](../project/PHX-G99_ARCHITECTURE_GATE.md)
