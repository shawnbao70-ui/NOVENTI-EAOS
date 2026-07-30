# PHX-G24 Gateway Knowledge HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** knowledge.openapi.yaml、ADR-0033、ADR-0039  
**退出门禁：** 薄适配；出处与授权仍由 Knowledge/Permission 裁决

## 1. 门禁目标

交付 Knowledge 实体/链接/检索/出处 HTTP 垂直切片。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway/routers/knowledge` |
| Permission | 共享 `app.state.permission` |
| Elevation | 禁止 body 覆盖上下文 |

## 3. Exit Criteria

1. 六条路由契约通过。  
2. G18–G23 仍绿。  
3. 完整回归通过。  
4. 不宣称 archive/share/OIDC 已交付。

## 4. Explicit Defer

archive / share HTTP；JWT/OIDC；商业 Marketplace
