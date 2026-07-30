# PHX-G27 Gateway Package Platform HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** package.openapi.yaml、ADR-0033、ADR-0042  
**退出门禁：** 薄适配；无业务规则；上下文不可提升

## 1. 门禁目标

交付 Package Platform 租户面 HTTP（manifest/install/surface/resolve），固定受信上下文与 Kernel 权限边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | `derive_tenant_context` only |
| Elevation | `reject_context_override` on bodies |
| Authority | PackageService + Permission |
| Economy | 不开放 Marketplace 商业路径 |

## 3. Exit Criteria

1. OpenAPI 所列 Package 路由契约通过。  
2. Kernel fork / reserved resource 仍由 Capability 拒绝。  
3. G18–G26 仍绿；完整回归通过。  
4. 不宣称 Marketplace 商业或 OIDC 已交付。

## 4. Explicit Defer

Marketplace 商业政策；JWT/OIDC；包热更新策略
