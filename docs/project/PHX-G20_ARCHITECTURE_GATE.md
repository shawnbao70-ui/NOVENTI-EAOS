# PHX-G20 Gateway Identity HTTP Surface Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** BOOK19、identity.openapi.yaml、ADR-0033、ADR-0035  
**退出门禁：** 网关不宿主业务规则；上下文不可由客户端提升

## 1. 门禁目标

在 G18 受信边界上交付 Identity HTTP 垂直切片，证明契约路径可到达 Kernel 服务。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway/routers/identity` |
| Service | 注入 `IdentityService` / Transactional* |
| Elevation | 禁止 body `tenant_id`/`platform_scope`；允许资源 `subject_id` |
| Adapters catalog | 仍为目录；不迁入 routers |

## 3. Exit Criteria

1. 五条 Identity 路由契约测试通过。  
2. G18 五条契约仍绿。  
3. 完整回归通过。  
4. 不宣称全量 Identity OpenAPI 或 OIDC 已交付。

## 4. Explicit Defer

AI/Governor/revoke HTTP、JWT/OIDC、其他域路由、商业 Marketplace
