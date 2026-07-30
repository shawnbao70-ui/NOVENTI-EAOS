# PHX-G29 Gateway AI Runtime HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** ai.openapi.yaml、ADR-0033、ADR-0044  
**退出门禁：** 薄适配；AI≠执行权；上下文不可提升

## 1. 门禁目标

交付 AI Runtime 租户面 HTTP（run/tool/memory/approval/commit），固定受信上下文与审批边界。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Context | `derive_tenant_context` only |
| Elevation | `reject_context_override` |
| Subject | Kernel 要求 AI subject；网关不伪造 |
| Wiring | AI 默认共享 Workflow + Knowledge reader |

## 3. Exit Criteria

1. OpenAPI 所列八路由契约通过。  
2. 非 AI subject 创建 run 被拒绝。  
3. 无审批 commit / high-impact 仍由 Kernel 拒绝。  
4. G18–G28 仍绿；完整回归通过。

## 4. Explicit Defer

Terminal HTTP；JWT/OIDC；商业 Marketplace
