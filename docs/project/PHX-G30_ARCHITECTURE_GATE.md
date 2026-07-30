# PHX-G30 Gateway Smart Terminal HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** terminal.openapi.yaml、ADR-0033、ADR-0045  
**退出门禁：** 薄适配；审批真相归 Workflow；上下文不可提升

## 1. 门禁目标

交付 Smart Terminal 租户面 HTTP（session/intent/preview/approval/commit），固定受信上下文与审批边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | `derive_tenant_context` only |
| Elevation | body `tenant_id`/`platform_scope` 拒绝；claimed_* 归 Capability |
| Approval truth | `present_approval` 只读 Workflow |
| Wiring | 默认共享 Workflow + Permission |

## 3. Exit Criteria

1. OpenAPI 所列十路由契约通过。  
2. claimed 不匹配 / high-impact 无审批仍拒绝。  
3. G18–G29 仍绿；完整回归通过。  
4. 不宣称完整 Terminal UI 或 OIDC 已交付。

## 4. Explicit Defer

完整 Terminal UI；JWT/OIDC；商业 Marketplace
