# PHX-G32 Gateway Organization Route Completions Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** organization.openapi.yaml、ADR-0047  
**退出门禁：** 薄适配；平台/租户面分离仍成立

## 1. 门禁目标

补齐 Organization 企业/单元/成员生命周期 HTTP。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | 租户面 `derive_tenant_context` |
| Platform | 不改 G25 平台面 |
| Authority | Kernel OrganizationService |

## 3. Exit Criteria

1. 扩展路由契约通过。  
2. G18–G31 仍绿；完整回归通过。  
3. 不宣称 OIDC / 商业 Marketplace / Terminal UI 已交付。

## 4. Explicit Defer

JWT/OIDC；商业 Marketplace；完整 Terminal UI
