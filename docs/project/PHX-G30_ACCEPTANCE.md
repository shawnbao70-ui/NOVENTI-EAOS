# PHX-G30 Gateway Smart Terminal HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；审批真相归 Workflow；上下文不可提升

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0045 + Architecture Gate |
| B | Terminal 十路由 + 序列化 + TERMINAL_* 错误映射 |
| C | claimed_* 提升拒绝 + low-impact commit |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- `/v1/terminal*` → `derive_tenant_context`
- Body 禁止 `tenant_id` / `platform_scope`；claimed_* 归 Capability
- 审批呈现只读 Workflow；high-impact 无审批不可 commit
- Smart Terminal 仍独立于 Core Kernel（`smart_terminal/`）

## 3. 自动化证据

- 本地完整回归：`383 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0045 |
| Constitution Review | 通过；Terminal 不进 Kernel |
| Cross-reference Review | 通过；OpenAPI `terminal.openapi.yaml` |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G29 仍绿 |
| Gap Analysis | 完整 Terminal UI 与 OIDC 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- 完整 Terminal UI（前端）
- JWT/OIDC 认证提供商
- Marketplace 商业政策

## 6. 证据索引

- [PHX-G30 Architecture Gate](PHX-G30_ARCHITECTURE_GATE.md)
- [ADR-0045](../decisions/ADR-0045-gateway-terminal-http-surface.md)
- [Terminal router](../../api/gateway/routers/terminal.py)
