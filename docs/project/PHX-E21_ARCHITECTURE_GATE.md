# PHX-E21 Event Webhook Transport Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Shared Event Capability / Event Bus  
**规范源：** EVENT_INTERFACE、ADR-0051  
**退出门禁：** Event Bus 拥有投递；Gateway 薄适配；SSRF 基础门禁

## 1. 门禁目标

为订阅增加可选 webhook 传输，闭合 T-0228 技术缺口。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Delivery owner | Event Bus handler / outbox path |
| Gateway | `delivery_url` 透传 |
| Persistence | Alembic `0021_event_webhook_e21` |
| Signing | 延后 |

## 3. Exit Criteria

1. Webhook 订阅 → enqueue → dispatch 触发 POST（测试 double）。  
2. 非法 URL 被拒绝；G26 no-op 路径仍绿。  
3. 完整回归与 PostgreSQL 通过。  
4. 不宣称签名产品化 / Broker / OIDC。

## 4. Explicit Defer

HMAC 签名；DNS rebinding 完整防护；外部 Broker；JWT/OIDC；商业 Marketplace
