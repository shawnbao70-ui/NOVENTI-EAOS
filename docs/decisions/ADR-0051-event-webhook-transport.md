# ADR-0051 — Event Webhook External Subscription Transport

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-E21  
**归属：** Shared Event Capability / Event Bus

## 背景

G26 HTTP `POST /subscriptions` 仅登记进程内 no-op handler。需要可选 webhook 投递，且投递所有权仍归 Event Bus（重试 / DLQ / 幂等不变）。

## 决策

### 1. Ownership

- Kernel `EventBus` 拥有 webhook 投递（`dispatch_due` → handler POST）
- Gateway 仅透传可选 `delivery_url`；无重试策略、无业务规则
- 落点：`kernel/event_bus/url_safety.py`、`webhook.py`；订阅表 `delivery_url`

### 2. 订阅语义

- 无 `delivery_url`：行为同 G26（HTTP no-op 或进程内 callable）
- 有 `delivery_url`：构建 webhook handler；URL 持久化以便进程重启后重建
- 复用 `(subscriber_id, event_id)` 幂等与既有 retry / DLQ

### 3. SSRF 基础门禁

- 默认要求 `https`
- `http` 仅允许 loopback（本地契约）
- 拒绝 URL 凭证、metadata / link-local / 私网 IP 字面量
- 不跟随 HTTP 重定向

### 4. Explicit Defer

- Webhook 签名 / HMAC 密钥产品化与轮换
- JWT/OIDC；外部 Broker / 多区域
- DNS rebinding 完整防护与企业 egress 策略产品化

## 关联

- [ADR-0041-gateway-event-http-surface.md](ADR-0041-gateway-event-http-surface.md)
- [ADR-0026-event-outbox-worker-dlq.md](ADR-0026-event-outbox-worker-dlq.md)
- [../project/PHX-E21_ARCHITECTURE_GATE.md](../project/PHX-E21_ARCHITECTURE_GATE.md)
