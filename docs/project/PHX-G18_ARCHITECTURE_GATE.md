# PHX-G18 API Gateway Foundation Architecture Gate

**日期：** 2026-07-18  
**状态：** Fully Accepted（实现已验收）  
**归属：** Platform API Gateway  
**规范源：** BOOK19、API_STANDARD、ADR-0032、ADR-0033  
**退出门禁：** 客户端无法提升安全上下文；API 不宿主业务规则

## 1. 门禁目标

交付最小 FastAPI 网关：健康检查、发布清单、适配器目录、受信上下文回显，证明上下文不可由客户端提升。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Ownership | `api/gateway` |
| Context | 仅受信头派生 |
| Elevation | 请求体字段忽略/拒绝 |
| Business rules | 不在网关内实现 |
| AuthN product | 延后；头注入模拟受信边界 |

## 3. Exit Criteria

1. 缺少受信头失败关闭。  
2. Body 中的 tenant/subject 不能改变派生上下文。  
3. `/v1/release` 与 Manifest 一致。  
4. 契约测试覆盖网关；完整回归通过。  
5. 不宣称全量 OpenAPI 路由或生产认证已交付。

## 4. Explicit Defer

全量资源路由、OIDC、业务包 API、商业 Marketplace 结算
