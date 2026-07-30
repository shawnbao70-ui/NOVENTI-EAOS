# ADR-0116 — Terminal Event Bus Stats Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G97  
**归属：** Smart Terminal / Event Bus

## 背景

P11/G26 已交付 Outbox / stats / dead-letters / replay HTTP 面。运维仍缺 Terminal 内薄探针。

## 决策

1. Terminal Admin 增加 Event delivery stats、List dead letters、Replay dead letter 薄控件。  
2. 仅调用既有 `/v1/events/stats`、`/v1/events/dead-letters`、`POST .../dead-letters/{id}/replay`。  
3. 租户受信上下文；禁止 body 提升。  
4. 不新增订阅/Webhook 配置 UI；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0011-event-delivery-persistence.md](ADR-0011-event-delivery-persistence.md)
- [../project/PHX-G97_ARCHITECTURE_GATE.md](../project/PHX-G97_ARCHITECTURE_GATE.md)
