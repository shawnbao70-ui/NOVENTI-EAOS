# ADR-0045 — Gateway Smart Terminal HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G30  
**归属：** Platform API Gateway

## 背景

PHX-T13 已交付 Smart Terminal（Session / Intent / Preview / Approval UX / Commit）。OpenAPI `terminal.openapi.yaml` 定义租户面 HTTP；网关需薄适配，不得宿主业务规则或伪造审批真相。

## 决策

### 1. 租户面上下文

- 全部 `/v1/terminal*` 使用 `derive_tenant_context`
- Body 经 `reject_context_override`（禁止 `tenant_id` / `platform_scope`）
- `claimed_tenant_id` / `claimed_subject_id` 仅作会话打开时的声明字段，由 SmartTerminalService 校验；不匹配 → `TERMINAL_CONTEXT_ELEVATION_DENIED`

### 2. 本切片路由

| Method | Path | Kernel |
|--------|------|--------|
| POST | `/v1/terminal/sessions` | `open_session` |
| GET | `/v1/terminal/sessions/{id}` | `get_session` |
| POST | `/v1/terminal/sessions/{id}` | `close_session` |
| POST | `/v1/terminal/intents` | `compose_intent` |
| GET | `/v1/terminal/intents/{id}` | `get_intent` |
| POST | `/v1/terminal/previews` | `build_preview` |
| GET | `/v1/terminal/previews/{id}` | `get_preview` |
| POST | `/v1/terminal/previews/{id}/approvals` | `request_approval` |
| GET | `/v1/terminal/previews/{id}/approvals` | `present_approval` |
| POST | `/v1/terminal/previews/{id}/commits` | `commit` |

### 3. 默认接线

- 默认 `SmartTerminalService(permission, workflow)`，与 AI/Workflow 共享 Permission + Workflow

### 4. Explicit Defer

- 完整 Terminal UI（前端）
- JWT/OIDC 产品化
- Marketplace 商业政策

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G30_ARCHITECTURE_GATE.md](../project/PHX-G30_ARCHITECTURE_GATE.md)
- [../api/terminal.openapi.yaml](../api/terminal.openapi.yaml)
