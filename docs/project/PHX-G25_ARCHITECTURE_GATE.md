# PHX-G25 Gateway Platform Tenant Lifecycle Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** organization.openapi.yaml、ADR-0033、ADR-0040  
**退出门禁：** 平台面仅由 `/platform/*` 派生；租户面不可提升

## 1. 门禁目标

交付平台租户创建/挂起/恢复 HTTP，并固定受信平台上下文边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Platform context | `derive_platform_context` 仅挂平台路由 |
| Elevation | 租户面仍 `platform_scope=False` |
| Authority | Kernel platform governor（非网关裁决） |

## 3. Exit Criteria

1. 三条平台路由契约通过。  
2. 租户面路由不能创建租户。  
3. G18–G24 仍绿；完整回归通过。  
4. 不宣称 OIDC 已交付。

## 4. Explicit Defer

JWT/OIDC；其他平台面；商业 Marketplace
