# PHX-G37 JWT/OIDC Trusted Context Acceptance

**日期：** 2026-07-19  
**状态：** Fully Accepted（HS256 基础面）  
**归属：** Platform API Gateway / Identity  
**退出门禁：** Bearer → ExecutionContext；开发头可关；伪造签名拒绝

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0053 + Architecture Gate |
| B | `api/gateway/auth_jwt.py` HS256 校验/签发 |
| C | `derive_tenant_context` / `derive_platform_context` Bearer 优先 |
| D | 环境开关：`EAOS_JWT_*` / `EAOS_ALLOW_DEV_CONTEXT_HEADERS` / `EAOS_REQUIRE_JWT` |
| E | 契约测试 + 七步自审 |

## 2. 核心不变量

- Body 仍不可提升 `tenant_id` / `platform_scope`
- 租户面 JWT 若带 `eaos_platform_scope=true` → 拒绝
- 平台面仅 `/v1/platform/*`；JWT 须 `eaos_platform_scope=true`
- Kernel 不解析原始密码或 IdP 协议

## 3. 自动化证据

- 本地完整回归：`410 passed`（`tests/contracts`；含 G37）
- PostgreSQL：本切片无 schema 变更；head 仍为 `0021_event_webhook_e21`
- Alembic head：`0021_event_webhook_e21`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0053 |
| Constitution Review | 通过；Gateway 认证边界 |
| Cross-reference Review | 通过；G18/G25 头路径仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；Annotated Header 默认值 |
| Gap Analysis | OIDC 登录页 / JWKS·RS256 / IdP 联邦显式延后 |
| Second-pass Review | Fully Accepted（HS256 基础面） |

## 5. Explicit Defer / Next Approved

- OIDC Authorization Code 登录页与 IdP 联邦
- JWKS / RS256 多密钥轮换
- Terminal UI Bearer 登录 UX（可选）
- **已批准待启：** PHX-M17 Marketplace 商业（需政策输入）

## 6. 证据索引

- [PHX-G37 Architecture Gate](PHX-G37_ARCHITECTURE_GATE.md)
- [ADR-0053](../decisions/ADR-0053-jwt-oidc-trusted-context.md)
- [PHX-M17 Gate](PHX-M17_ARCHITECTURE_GATE.md)
