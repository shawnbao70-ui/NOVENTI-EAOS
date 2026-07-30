# PHX-G27 Gateway Package Platform HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；无业务规则；上下文不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0042 + Architecture Gate |
| B | Package 七路由 + 序列化 + PACKAGE_* 错误映射 |
| C | 契约测试（含 kernel fork 拒绝）+ 七步自审 |

## 2. 核心不变量

- `/v1/packages*` → `derive_tenant_context`
- Body 禁止 `tenant_id` / `platform_scope` 覆盖
- Kernel fork / reserved resource 仍由 Capability 拒绝
- 不开放 Marketplace 商业路径

## 3. 自动化证据

- 本地完整回归：`369 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0042 |
| Constitution Review | 通过；薄适配 / 无业务宿主 |
| Cross-reference Review | 通过；OpenAPI `package.openapi.yaml` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G26 仍绿 |
| Gap Analysis | Marketplace 商业与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Marketplace 商业/法律门禁
- JWT/OIDC 认证提供商
- 包热更新 / 多版本并存策略变更

## 6. 证据索引

- [PHX-G27 Architecture Gate](PHX-G27_ARCHITECTURE_GATE.md)
- [ADR-0042](../decisions/ADR-0042-gateway-package-http-surface.md)
- [Package router](../../api/gateway/routers/package.py)
