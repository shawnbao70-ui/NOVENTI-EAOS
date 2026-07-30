# ADR-0043 — Gateway Twin & Brain HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G28  
**归属：** Platform API Gateway

## 背景

PHX-E15 已交付 Digital Twin 与 Enterprise Brain（建议与执行权分离）。OpenAPI `brain.openapi.yaml` 定义租户面 HTTP；网关需薄适配，不得把 Twin/Brain 输出提升为执行授权。

## 决策

### 1. 租户面上下文

- `/v1/twin*` 与 `/v1/brain*` 均使用 `derive_tenant_context`
- Body 经 `reject_context_override`
- 权限仍由 TwinService / BrainService + Permission 裁决

### 2. 本切片路由

| Method | Path | Kernel |
|--------|------|--------|
| POST | `/v1/twin/snapshots` | `upsert_snapshot` |
| GET | `/v1/twin/snapshots/{id}` | `get_snapshot` |
| POST | `/v1/twin/snapshots/{id}/authorize` | `authorize_from_twin`（恒拒绝） |
| POST | `/v1/brain/insights` | `publish_insight` |
| GET | `/v1/brain/insights/{id}` | `get_insight` |
| POST | `/v1/brain/insights/{id}/execute` | `request_execution`（恒拒绝） |

### 3. Fail-closed 执行路径

`authorize` / `execute` 必须映射为 HTTP 403（`TWIN_EXECUTION_FORBIDDEN` / `BRAIN_EXECUTION_FORBIDDEN`），网关不得短路为成功。

### 4. Explicit Defer

- JWT/OIDC 产品化
- Marketplace 商业政策
- AI Runtime / Terminal HTTP（后续切片）

## 关联

- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)
- [../project/PHX-G28_ARCHITECTURE_GATE.md](../project/PHX-G28_ARCHITECTURE_GATE.md)
- [../api/brain.openapi.yaml](../api/brain.openapi.yaml)
