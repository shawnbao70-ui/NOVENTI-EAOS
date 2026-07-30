# ADR-0117 — Terminal Event Dispatch Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G98  
**归属：** Smart Terminal / Event Bus

## 背景

G97 已提供 stats / DLQ / replay 薄探针。运维仍缺 Terminal 内触发 `dispatch_due` 与按 id 查看事件信封的薄调用面。

## 决策

1. Terminal Admin 增加 Dispatch due（`worker_id` + 可选 `limit`）与 Get event 薄控件。  
2. 仅调用既有 `POST /v1/events/dispatch` 与 `GET /v1/events/{event_id}`。  
3. 租户受信上下文；禁止 body 提升。  
4. 不新增订阅/Webhook 配置 UI；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0116-terminal-event-bus-stats.md](ADR-0116-terminal-event-bus-stats.md)
- [../project/PHX-G98_ARCHITECTURE_GATE.md](../project/PHX-G98_ARCHITECTURE_GATE.md)
