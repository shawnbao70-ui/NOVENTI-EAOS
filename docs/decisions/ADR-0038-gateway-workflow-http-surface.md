# ADR-0038 — Gateway Workflow HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G23  
**归属：** Platform API Gateway

## 背景

G20–G22 已交付 Identity / Organization / Permission HTTP 薄适配。Workflow 是下一成熟 Kernel 面。

## 决策

### 1. 本切片路由

对齐 `docs/api/workflow.openapi.yaml`：

- `POST /v1/workflow/definitions`
- `POST /v1/workflow/instances`
- `GET /v1/workflow/instances/{instanceId}`
- `POST /v1/workflow/instances/{instanceId}/tasks/{taskId}/approval`
- `POST /v1/workflow/instances/{instanceId}/tasks/{taskId}/rejection`
- `GET /v1/workflow/tasks`

### 2. 组合

- 默认 `WorkflowService(app.state.permission)`，与 Permission 共享同一服务实例
- Approve/Reject 将 OpenAPI `expected_task_version` 映射为服务 `expected_version`
- Body 禁止 `tenant_id` / `platform_scope`

### 3. Explicit Defer

deprecate / signal / cancel / compensate / escalate HTTP；OIDC；平台面

## 关联

- [ADR-0037-gateway-permission-http-surface.md](ADR-0037-gateway-permission-http-surface.md)
- [../project/PHX-G23_ARCHITECTURE_GATE.md](../project/PHX-G23_ARCHITECTURE_GATE.md)
