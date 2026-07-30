# PHX-G28 Gateway Twin & Brain HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；建议≠执行；上下文不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0043 + Architecture Gate |
| B | Twin 三路由 + Brain 三路由 + 序列化 |
| C | authorize/execute fail-closed（HTTP 403） |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `/v1/twin*` / `/v1/brain*` → `derive_tenant_context`
- Body 禁止 `tenant_id` / `platform_scope` 覆盖
- Twin authorize / Brain execute 恒拒绝
- Brain 默认以 TwinService 为 twin_reader

## 3. 自动化证据

- 本地完整回归：`374 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0043 |
| Constitution Review | 通过；建议与执行权分离 |
| Cross-reference Review | 通过；OpenAPI `brain.openapi.yaml` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G27 仍绿 |
| Gap Analysis | AI/Terminal HTTP 与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- AI Runtime HTTP
- Terminal HTTP
- JWT/OIDC 认证提供商
- Marketplace 商业政策

## 6. 证据索引

- [PHX-G28 Architecture Gate](PHX-G28_ARCHITECTURE_GATE.md)
- [ADR-0043](../decisions/ADR-0043-gateway-twin-brain-http-surface.md)
- [Twin router](../../api/gateway/routers/twin.py)
- [Brain router](../../api/gateway/routers/brain.py)
