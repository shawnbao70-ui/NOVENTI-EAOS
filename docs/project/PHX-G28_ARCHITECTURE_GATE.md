# PHX-G28 Gateway Twin & Brain HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** brain.openapi.yaml、ADR-0033、ADR-0043  
**退出门禁：** 薄适配；建议≠执行；上下文不可提升

## 1. 门禁目标

交付 Twin / Brain 租户面 HTTP，并固定执行路径 fail-closed。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | `derive_tenant_context` only |
| Elevation | `reject_context_override` |
| Execution | authorize/execute → 403 |
| Brain twin_ref | 默认注入 TwinService 为 reader |

## 3. Exit Criteria

1. OpenAPI 所列六路由契约通过。  
2. authorize/execute 恒 403。  
3. G18–G27 仍绿；完整回归通过。  
4. 不宣称 AI/Terminal/OIDC/商业 Marketplace 已交付。

## 4. Explicit Defer

AI Runtime HTTP；Terminal HTTP；JWT/OIDC；商业 Marketplace
