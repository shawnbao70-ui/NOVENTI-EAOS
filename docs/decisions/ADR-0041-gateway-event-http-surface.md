# ADR-0041 — Gateway Event Bus HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G26  
**归属：** Platform API Gateway

## 背景

PHX-P11 已交付 Event Bus（outbox、dispatch、DLQ、stats）。OpenAPI `event.openapi.yaml` 定义租户面 HTTP；网关需薄适配，不托管投递策略或业务规则。

## 决策

### 1. 租户面上下文

- 全部 `/v1/events*` 使用 `derive_tenant_context`
- Body 经 `reject_context_override`；禁止 `tenant_id` / `platform_scope` 提升
- 权限仍由 Kernel `EventBus` + `PermissionService`（`event_stream`）裁决

### 2. 本切片路由

| Method | Path | Kernel |
|--------|------|--------|
| POST | `/v1/events` | `publish` |
| POST | `/v1/events/outbox` | `enqueue` |
| POST | `/v1/events/dispatch` | `dispatch_due` |
| GET | `/v1/events/{eventId}` | `get_event` |
| POST | `/v1/events/{eventId}/replay` | `replay` |
| POST | `/v1/events/subscriptions` | `subscribe`（见下） |
| GET | `/v1/events/stats` | `get_delivery_stats` |
| GET | `/v1/events/dead-letters` | `list_dead_letters` |
| POST | `/v1/events/dead-letters/{id}/replay` | `replay_dead_letter` |

### 3. HTTP subscribe 语义

HTTP 无法传递可调用 handler。网关对 `POST /subscriptions` 注册 **进程内 no-op handler**，仅完成订阅登记与审计；真实投影/副作用 handler 仍由进程内 `EventBus.subscribe(...)`（或后续 webhook 传输）提供。不在网关内实现业务投递逻辑。

### 4. Explicit Defer

- Webhook / 外部订阅传输
- JWT/OIDC 产品化
- Marketplace 商业政策

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G26_ARCHITECTURE_GATE.md](../project/PHX-G26_ARCHITECTURE_GATE.md)
- [../api/event.openapi.yaml](../api/event.openapi.yaml)
