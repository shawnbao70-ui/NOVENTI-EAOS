# PHX-G25 Gateway Platform Tenant Lifecycle Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 平台面仅由 `/platform/*` 派生；租户面不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0040 + Architecture Gate |
| B | `derive_platform_context` |
| C | 三条平台租户路由 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `/v1/platform/*` → `platform_scope=True`，`tenant_id=None`
- 租户面仍 `derive_tenant_context`（`platform_scope=False`）
- 权限仍由 Kernel platform governor 裁决
- Body 禁止 `tenant_id` / `platform_scope` 覆盖

## 3. 自动化证据

- 本地完整回归：`358 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0040 |
| Constitution Review | 通过；平台/租户面分离 |
| Cross-reference Review | 通过；OpenAPI `/platform/tenants*` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G24 仍绿 |
| Gap Analysis | OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- JWT/OIDC 认证提供商
- 其他平台面能力
- Marketplace 商业政策

## 6. 证据索引

- [PHX-G25 Architecture Gate](PHX-G25_ARCHITECTURE_GATE.md)
- [ADR-0040](../decisions/ADR-0040-gateway-platform-tenant-http.md)
- [Platform Organization router](../../api/gateway/routers/platform_organization.py)
