# PHX-G22 Gateway Permission HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** permission.openapi.yaml、ADR-0033、ADR-0037  
**退出门禁：** 薄适配；Evaluate 不可 body 冒充 principal

## 1. 门禁目标

交付 Permission 策略/授权/评估 HTTP 垂直切片。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway/routers/permission` |
| Evaluate principal | 仅受信头 subject |
| Elevation | 禁止 body 覆盖上下文 |

## 3. Exit Criteria

1. 七条路由契约通过。  
2. G18–G21 仍绿。  
3. 完整回归通过。  
4. 不宣称 deprecate/delegate/OIDC 已交付。

## 4. Explicit Defer

Policy deprecation HTTP、Grant delegation HTTP、JWT/OIDC、商业 Marketplace
