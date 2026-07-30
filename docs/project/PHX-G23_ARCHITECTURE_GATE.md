# PHX-G23 Gateway Workflow HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** workflow.openapi.yaml、ADR-0033、ADR-0038  
**退出门禁：** 薄适配；审批权限仍由 Kernel/Permission 裁决

## 1. 门禁目标

交付 Workflow 定义/启动/查询/审批 HTTP 垂直切片。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway/routers/workflow` |
| Permission | 共享 `app.state.permission` |
| Elevation | 禁止 body 覆盖上下文 |

## 3. Exit Criteria

1. 六条路由契约通过。  
2. G18–G22 仍绿。  
3. 完整回归通过。  
4. 不宣称 signal/cancel/compensate/escalate 已交付。

## 4. Explicit Defer

signal / cancel / compensate / escalate / deprecate HTTP；JWT/OIDC；商业 Marketplace
