# PHX-G26 Gateway Event Bus HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** event.openapi.yaml、ADR-0033、ADR-0041  
**退出门禁：** 薄适配；无业务规则；上下文不可提升

## 1. 门禁目标

交付 Event Bus 租户面 HTTP（publish/outbox/dispatch/get/replay/subscribe/stats/DLQ），固定受信上下文与 Kernel 权限边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | `derive_tenant_context` only |
| Elevation | `reject_context_override` on bodies |
| Subscribe | HTTP 登记 no-op handler；真实 handler 进程内 |
| Authority | Kernel EventBus + Permission |

## 3. Exit Criteria

1. OpenAPI 所列事件路由契约通过。  
2. 无受信头 → 401；body 提升 → 拒绝。  
3. G18–G25 仍绿；完整回归通过。  
4. 不宣称 webhook/OIDC/商业 Marketplace 已交付。

## 4. Explicit Defer

Webhook 订阅传输；JWT/OIDC；商业 Marketplace
