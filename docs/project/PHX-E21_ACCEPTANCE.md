# PHX-E21 Event Webhook Transport Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Shared Event Capability / Event Bus  
**退出门禁：** Event Bus 拥有投递；Gateway 薄适配；SSRF 基础门禁

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0051 + Architecture Gate |
| B | `url_safety` + `webhook` 传输；`EventBus.subscribe(delivery_url=…)` |
| C | Alembic `0021_event_webhook_e21`；OpenAPI `delivery_url` |
| D | Gateway 透传；契约测试 + 七步自审 |

## 2. 核心不变量

- 投递仍经 outbox / retry / DLQ / `(subscriber_id, event_id)`
- Gateway 无业务规则与重试策略
- HTTPS（loopback http 仅测试）；拒私网 / metadata / URL 凭证
- 无签名产品化；无外部 Broker

## 3. 自动化证据

- 本地完整回归：`402 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0021_event_webhook_e21`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0051 |
| Constitution Review | 通过；Event 拥有投递 |
| Cross-reference Review | 通过；OpenAPI / EVENT_INTERFACE |
| Documentation Review | 通过 |
| Consistency Review | 通过；G26 no-op 仍绿 |
| Gap Analysis | 签名 / Broker / OIDC / 商业显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Webhook HMAC 签名与密钥轮换
- DNS rebinding 完整防护 / 企业 egress 产品化
- 外部 Broker；JWT/OIDC；Marketplace 商业政策

## 6. 证据索引

- [PHX-E21 Architecture Gate](PHX-E21_ARCHITECTURE_GATE.md)
- [ADR-0051](../decisions/ADR-0051-event-webhook-transport.md)
