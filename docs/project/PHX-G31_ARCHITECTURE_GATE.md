# PHX-G31 Gateway Domain Route Completions Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** workflow/knowledge/permission OpenAPI、ADR-0046  
**退出门禁：** 薄适配；无业务规则；既有主路径仍绿

## 1. 门禁目标

补齐 Workflow / Knowledge / Permission 已延后的扩展 HTTP 路由。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Scope | 仅 OpenAPI 已定义且 Kernel 已实现的扩展操作 |
| Context | 租户面不变 |
| Org fill-in | 另切片 |

## 3. Exit Criteria

1. 扩展路由契约通过。  
2. G18–G30 仍绿；完整回归通过。  
3. 不宣称 OIDC / 商业 Marketplace / Terminal UI 已交付。

## 4. Explicit Defer

Organization 扩展；JWT/OIDC；商业 Marketplace；Terminal UI
