# PHX-G20 Gateway Identity HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 网关不宿主业务规则；上下文不可由客户端提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0035 + Architecture Gate |
| B | Identity 五路由薄适配 + DI |
| C | 上下文覆盖拒绝 vs 资源 subject_id 区分 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 路径对齐 `identity.openapi.yaml`：subjects / credentials / sessions / validation
- `ExecutionContext` 仅受信头；body 禁止 `tenant_id` / `platform_scope`
- 绑定凭证的资源 `subject_id` 允许（非上下文提升）
- `ttl_minutes` → `ttl_seconds`；服务错误经 `raise_for_result` 映射
- 默认注入内存 `IdentityService`；可替换 Transactional*

## 3. 自动化证据

- 本地完整回归：`322 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0035；落点 `api/gateway/routers/identity` |
| Constitution Review | 通过；BOOK19 薄适配 |
| Cross-reference Review | 通过；OpenAPI 路径对齐 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18 契约仍绿 |
| Gap Analysis | AI/Governor/OIDC/其他域显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Identity AI / Governor / revoke HTTP
- JWT/OIDC；其他域全量 HTTP
- Marketplace 商业结算

## 6. 证据索引

- [PHX-G20 Architecture Gate](PHX-G20_ARCHITECTURE_GATE.md)
- [ADR-0035](../decisions/ADR-0035-gateway-identity-http-surface.md)
- [identity.openapi.yaml](../api/identity.openapi.yaml)
- [Gateway Identity router](../../api/gateway/routers/identity.py)
