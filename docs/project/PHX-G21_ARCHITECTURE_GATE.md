# PHX-G21 Gateway Organization HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** organization.openapi.yaml、ADR-0033、ADR-0036  
**退出门禁：** 租户面薄适配；不开放平台上下文提升

## 1. 门禁目标

在 G18/G20 受信边界上交付 Organization 租户面 HTTP 垂直切片。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway/routers/organization` |
| Plane | 仅租户面 |
| Platform HTTP | 延后 |
| Elevation | 禁止 body 覆盖上下文 |

## 3. Exit Criteria

1. 六条租户面路由契约通过。  
2. G18/G20 契约仍绿。  
3. 完整回归通过。  
4. 不宣称平台租户 HTTP 或 OIDC 已交付。

## 4. Explicit Defer

平台租户生命周期、其余 Organization 操作、OIDC、商业 Marketplace
