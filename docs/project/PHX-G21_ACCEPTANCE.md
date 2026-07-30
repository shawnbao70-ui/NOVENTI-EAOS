# PHX-G21 Gateway Organization HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 租户面薄适配；不开放平台上下文提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0036 + Architecture Gate |
| B | 六条租户面 Organization 路由 |
| C | ORG_* 错误映射 + DI |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 路径对齐 OpenAPI：`/tenants/{id}`、`/enterprises`、`/organization-units`、`/memberships`
- 仅租户面；平台租户生命周期 HTTP 延后
- Body 禁止 `tenant_id` / `platform_scope`；资源 `subject_id` 允许
- 默认 `OrganizationService()`；测试可注入 eligibility

## 3. 自动化证据

- 本地完整回归：`331 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0036 |
| Constitution Review | 通过；薄适配、无平台提升 |
| Cross-reference Review | 通过；OpenAPI 路径对齐 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18/G20 仍绿 |
| Gap Analysis | 平台租户 HTTP / 其余 Org 操作延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- `POST /v1/platform/tenants*` 与 suspension
- membership 转移/结束、unit tree/status
- JWT/OIDC；商业 Marketplace

## 6. 证据索引

- [PHX-G21 Architecture Gate](PHX-G21_ARCHITECTURE_GATE.md)
- [ADR-0036](../decisions/ADR-0036-gateway-organization-http-surface.md)
- [organization.openapi.yaml](../api/organization.openapi.yaml)
- [Gateway Organization router](../../api/gateway/routers/organization.py)
