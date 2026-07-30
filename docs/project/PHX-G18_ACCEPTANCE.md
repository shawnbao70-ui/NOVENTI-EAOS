# PHX-G18 API Gateway Foundation Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 客户端无法提升安全上下文；网关不宿主业务规则

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0033 + Architecture Gate |
| B | `api/gateway` 最小 FastAPI 应用与受信头派生 |
| C | 健康 / Release / Adapters / Context echo；商业定价 HTTP 失败关闭 |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `ExecutionContext` 仅从受信头派生：`X-EAOS-Subject-Id` / `X-EAOS-Subject-Type` / `X-EAOS-Tenant-Id` / `X-Correlation-Id`
- 请求体中的 `tenant_id` / `subject_id` / `platform_scope` / `session_id` → `TERMINAL_CONTEXT_ELEVATION_DENIED`
- `platform_scope` 恒为 false（本切片不开放平台面）
- `/v1/release` 与 Release Manifest 版本及 Alembic head 一致
- Marketplace 定价 HTTP 路径 → `403 MARKETPLACE_COMMERCIAL_POLICY_REQUIRED`
- 契约真相源仍为 `docs/api/*.openapi.yaml`；网关不做业务规则宿主

## 3. 自动化证据

- 本地完整回归：`305 passed`（`tests/contracts`，含 5 项网关契约）
- 专用 PostgreSQL 17：`19 passed`（无新迁移；head 仍为 `0020_marketplace_m16`）
- Alembic head：`0020_marketplace_m16`
- 可选依赖：`noventi-eaos[api]`（FastAPI / httpx / uvicorn）

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0033；落点 `api/gateway` |
| Constitution Review | 通过；BOOK19 / API_STANDARD；不宿主业务规则 |
| Cross-reference Review | 通过；与 ADR-0032 adapters / Manifest 对齐 |
| Documentation Review | 通过；Gate / Acceptance / api README |
| Consistency Review | 通过；版本与 head 未漂移 |
| Gap Analysis | 最小网关闭环；全量 OpenAPI 路由与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 完整 OpenAPI 全量路由实现
- JWT / OIDC 认证提供商产品化
- 业务包 HTTP 面
- Marketplace 商业结算 API 产品化（仍需另批人工批准）

## 6. 证据索引

- [PHX-G18 Architecture Gate](PHX-G18_ARCHITECTURE_GATE.md)
- [ADR-0033](../decisions/ADR-0033-api-gateway-boundary.md)
- [api/gateway](../../api/gateway/app.py)
- [Gateway contracts](../../tests/contracts/test_api_gateway_g18.py)
- [Release Manifest](../release/RELEASE_MANIFEST.yaml)
