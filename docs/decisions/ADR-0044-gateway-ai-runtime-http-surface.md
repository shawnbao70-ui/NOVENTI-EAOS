# ADR-0044 — Gateway AI Runtime HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G29  
**归属：** Platform API Gateway

## 背景

PHX-A12 已交付 AI Runtime（Agent Run / Tool / Memory / Approval Bridge）。OpenAPI `ai.openapi.yaml` 定义租户面 HTTP；网关需薄适配，不得把 AI 输出直接提升为执行权。

## 决策

### 1. 租户面上下文

- 全部 `/v1/ai*` 使用 `derive_tenant_context`
- Body 经 `reject_context_override`
- AI 操作主体类型仍由 Kernel 校验（`ai` / `ai_employee`）
- 权限与审批桥接仍归 AIRuntimeService + Workflow + Permission

### 2. 本切片路由

| Method | Path | Kernel |
|--------|------|--------|
| POST | `/v1/ai/runs` | `create_agent_run` |
| GET | `/v1/ai/runs/{id}` | `get_agent_run` |
| POST | `/v1/ai/tools` | `register_tool` |
| POST | `/v1/ai/runs/{id}/tools/invocations` | `invoke_tool` |
| POST | `/v1/ai/runs/{id}/memory` | `write_memory` |
| GET | `/v1/ai/runs/{id}/memory/{key}` | `read_memory` |
| POST | `/v1/ai/runs/{id}/approvals` | `request_approval` |
| POST | `/v1/ai/runs/{id}/commits` | `commit_action` |

### 3. 默认接线

- 默认 `AIRuntimeService(permission, workflow, knowledge_reader=knowledge)`
- 与 Workflow / Knowledge 共享同一 Permission 实例

### 4. Explicit Defer

- JWT/OIDC 产品化
- Terminal HTTP / UI
- Marketplace 商业政策
- knowledge access HTTP（Capability 内方法，OpenAPI 未单列）

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G29_ARCHITECTURE_GATE.md](../project/PHX-G29_ARCHITECTURE_GATE.md)
- [../api/ai.openapi.yaml](../api/ai.openapi.yaml)
