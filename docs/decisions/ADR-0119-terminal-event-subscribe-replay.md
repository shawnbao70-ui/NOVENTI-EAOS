# ADR-0119 — Terminal Event Subscribe/Replay Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G100  
**归属：** Smart Terminal / Event Bus

## 背景

G97–G99 已覆盖 stats/DLQ/dispatch/get/enqueue/publish。运维仍缺 Terminal 内订阅与按事件 id 重放的薄调用面。

## 决策

1. Terminal Admin 增加 Subscribe 与 Replay event 薄控件。  
2. 仅调用既有 `POST /v1/events/subscriptions` 与 `POST /v1/events/{event_id}/replay`。  
3. 订阅 body：`subscriber_id` + `event_name`；可选 `delivery_url`；**不**在 Terminal 采集/回显 `signing_secret`。  
4. 禁止 body 上下文提升；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  
- Webhook signing_secret 管理台  

## 关联

- [ADR-0116-terminal-event-bus-stats.md](ADR-0116-terminal-event-bus-stats.md)
- [ADR-0118-terminal-event-enqueue-publish.md](ADR-0118-terminal-event-enqueue-publish.md)
- [../project/PHX-G100_ARCHITECTURE_GATE.md](../project/PHX-G100_ARCHITECTURE_GATE.md)
