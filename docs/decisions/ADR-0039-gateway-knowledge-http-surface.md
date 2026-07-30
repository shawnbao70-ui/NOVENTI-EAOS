# ADR-0039 — Gateway Knowledge HTTP Surface

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G24  
**归属：** Platform API Gateway

## 背景

G20–G23 已交付 Identity / Organization / Permission / Workflow HTTP 薄适配。Knowledge 为 Shared Platform Capability，OpenAPI 与服务已成熟。

## 决策

### 1. 本切片路由

对齐 `docs/api/knowledge.openapi.yaml`：

- `POST|GET /v1/knowledge/entities`
- `GET /v1/knowledge/entities/{entityId}`
- `POST /v1/knowledge/links`
- `GET /v1/knowledge/search`
- `GET /v1/knowledge/provenance/{subjectKind}/{subjectId}`

### 2. 组合

- 默认 `KnowledgeService(app.state.permission)`
- Body 禁止 `tenant_id` / `platform_scope`
- query/search/provenance 列表响应按 OpenAPI 使用 `{ok, data}` 包装

### 3. Explicit Defer

archive / share HTTP；OIDC；平台面；商业 Marketplace

## 关联

- [ADR-0038-gateway-workflow-http-surface.md](ADR-0038-gateway-workflow-http-surface.md)
- [../project/PHX-G24_ARCHITECTURE_GATE.md](../project/PHX-G24_ARCHITECTURE_GATE.md)
