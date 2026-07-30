# PHX-G23 Gateway Workflow HTTP Surface Acceptance

**日期：** 2026-07-18  
**状态：** Fully Accepted  
**归属：** Platform API Gateway  
**退出门禁：** 薄适配；审批权限仍由 Kernel/Permission 裁决

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0038 + Architecture Gate |
| B | 六条 Workflow 路由薄适配 |
| C | WORKFLOW_* 错误映射；与 Permission 共享 DI |
| D | 契约测试 + 七步自审 |

## 2. 核心不变量

- 路径对齐 `workflow.openapi.yaml`
- 默认 `WorkflowService(app.state.permission)`
- Approve/Reject 映射 `expected_task_version` → 服务 `expected_version`
- Body 禁止 `tenant_id` / `platform_scope`

## 3. 自动化证据

- 本地完整回归：`346 passed`（`tests/contracts`）
- 专用 PostgreSQL 17：`19 passed`
- Alembic head：`0020_marketplace_m16`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0038 |
| Constitution Review | 通过；审批真相源仍在 Workflow Kernel |
| Cross-reference Review | 通过 |
| Documentation Review | 通过 |
| Consistency Review | 通过；G18–G22 仍绿 |
| Gap Analysis | signal/cancel/compensate/escalate 显式延后 |
| Second-pass Review | Fully Accepted |

## 5. Explicit Defer

- deprecate / signal / cancel / compensate / escalate HTTP
- JWT/OIDC；平台面；商业 Marketplace

## 6. 证据索引

- [PHX-G23 Architecture Gate](PHX-G23_ARCHITECTURE_GATE.md)
- [ADR-0038](../decisions/ADR-0038-gateway-workflow-http-surface.md)
- [workflow.openapi.yaml](../api/workflow.openapi.yaml)
- [Gateway Workflow router](../../api/gateway/routers/workflow.py)
