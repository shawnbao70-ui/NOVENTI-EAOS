# PHX-G32 Gateway Organization Route Completions Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；租户/平台面分离仍成立

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0047 + Architecture Gate |
| B | Enterprise：GET / close / suspend / reactivate |
| C | Org Unit：GET tree；PUT status |
| D | Membership：end / transfer unit / suspend / reactivate |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- 扩展路由仍走 `derive_tenant_context` + `reject_context_override`
- 业务语义仍归 Kernel OrganizationService
- 平台租户生命周期仍仅 `/v1/platform/*`（G25）
- G18–G31 主路径不回归

## 3. 自动化证据

- 本地完整回归：`393 passed`（`tests/contracts`；含 G32 + G34）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0047 |
| Constitution Review | 通过；薄适配 |
| Cross-reference Review | 通过；对应 OpenAPI 扩展路径 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G31 仍绿 |
| Gap Analysis | Terminal UI / OIDC / 商业 Marketplace 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 完整 Terminal UI
- JWT/OIDC；Marketplace 商业政策

## 6. 证据索引

- [PHX-G32 Architecture Gate](PHX-G32_ARCHITECTURE_GATE.md)
- [ADR-0047](../decisions/ADR-0047-gateway-organization-route-completions.md)
