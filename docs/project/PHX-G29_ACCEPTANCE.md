# PHX-G29 Gateway AI Runtime HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；AI≠执行权；上下文不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0044 + Architecture Gate |
| B | AI 八路由 + 序列化 + AI_* 错误映射 |
| C | 默认 AI 共享 Workflow + Knowledge reader |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `/v1/ai*` → `derive_tenant_context`
- Body 禁止 `tenant_id` / `platform_scope` 覆盖
- AI subject 校验仍归 Kernel（非 AI 创建 run → 403）
- commit / high-impact 仍需审批桥接

## 3. 自动化证据

- 本地完整回归：`378 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0044 |
| Constitution Review | 通过；AI Runtime 不在 Core Kernel |
| Cross-reference Review | 通过；OpenAPI `ai.openapi.yaml` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G28 仍绿 |
| Gap Analysis | Terminal HTTP 与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- Terminal HTTP / UI
- JWT/OIDC 认证提供商
- Marketplace 商业政策

## 6. 证据索引

- [PHX-G29 Architecture Gate](PHX-G29_ARCHITECTURE_GATE.md)
- [ADR-0044](../decisions/ADR-0044-gateway-ai-runtime-http-surface.md)
- [AI router](../../api/gateway/routers/ai.py)
