# PHX-G24 Gateway Knowledge HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；出处与授权仍由 Knowledge/Permission 裁决

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0039 + Architecture Gate |
| B | 六条 Knowledge 路由薄适配 |
| C | KNOWLEDGE_* 错误映射；与 Permission 共享 DI |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 路径对齐 `knowledge.openapi.yaml`
- 默认 `KnowledgeService(app.state.permission)`
- query/search/provenance 使用 `{ok, data}` 列表包装
- Body 禁止 `tenant_id` / `platform_scope`；出处字段必填由 Kernel 强制

## 3. 自动化证据

- 本地完整回归：`352 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0039 |
| Constitution Review | 通过；知识主权与出处仍在 Shared Capability |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G23 仍绿 |
| Gap Analysis | archive/share HTTP 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- archive / share HTTP
- JWT/OIDC；平台面；商业 Marketplace

## 6. 证据索引

- [PHX-G24 Architecture Gate](PHX-G24_ARCHITECTURE_GATE.md)
- [ADR-0039](../decisions/ADR-0039-gateway-knowledge-http-surface.md)
- [knowledge.openapi.yaml](../api/knowledge.openapi.yaml)
- [Gateway Knowledge router](../../api/gateway/routers/knowledge.py)
