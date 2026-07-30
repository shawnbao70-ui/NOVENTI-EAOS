# PHX-G26 Gateway Event Bus HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；无业务规则；上下文不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0041 + Architecture Gate |
| B | Event 九路由 + 序列化 + EVENT_* 错误映射 |
| C | HTTP subscribe = no-op handler 登记（ADR 明示） |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `/v1/events*` → `derive_tenant_context`
- Body 禁止 `tenant_id` / `platform_scope` 覆盖
- 权限仍由 Kernel EventBus + Permission 裁决
- 网关不托管投递策略或业务副作用

## 3. 自动化证据

- 本地完整回归：`365 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0041 |
| Constitution Review | 通过；薄适配 / 无业务宿主 |
| Cross-reference Review | 通过；OpenAPI `event.openapi.yaml` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G25 仍绿 |
| Gap Analysis | Webhook 订阅与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Webhook / 外部订阅传输
- JWT/OIDC 认证提供商
- Marketplace 商业政策

## 6. 证据索引

- [PHX-G26 Architecture Gate](PHX-G26_ARCHITECTURE_GATE.md)
- [ADR-0041](../decisions/ADR-0041-gateway-event-http-surface.md)
- [Event router](../../api/gateway/routers/event.py)
