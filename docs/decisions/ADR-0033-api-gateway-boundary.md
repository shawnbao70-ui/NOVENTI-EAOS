# ADR-0033 — API Gateway 边界（Post-Foundation）

**状态：** Accepted  
**日期：** 2026-07-18  
**里程碑：** PHX-G18  
**归属：** Platform API Gateway

## 背景

PHX-R17 已交付契约目录与 SDK，并显式延后 FastAPI。Foundation 通过后可引入最小 HTTP 网关，但不得成为业务规则宿主，也不得接受客户端自报安全上下文。

## 决策

### 1. 落点

- 实现：`api/gateway/`
- 契约真相源仍为 `docs/api/*.openapi.yaml`
- Gateway 只做传输适配与受信上下文派生

### 2. 受信上下文

- 网关从**受信边界头**派生 `ExecutionContext`：
  - `X-EAOS-Subject-Id`
  - `X-EAOS-Subject-Type`
  - `X-EAOS-Tenant-Id`（租户面）
  - `X-Correlation-Id`
- 请求体/查询参数中的 `tenant_id` / `subject_id` / `platform_scope` **不得**覆盖派生上下文
- `platform_scope` 默认 false；本切片不开放平台面提升

### 3. 最小路由面

- `GET /v1/health`
- `GET /v1/release`
- `GET /v1/adapters`
- `GET /v1/context`（回显派生上下文，用于门禁证明）
- 商业 Marketplace 定价路径若暴露则保持失败关闭

### 4. 依赖

- FastAPI 作为可选 extra：`noventi-eaos[api]`
- 生产部署拓扑 Foundation 见 ADR-0068 / PHX-G49；无认证提供商产品化以外的联邦 UI（头注入仅开发边界）

## Explicit Defer

- 完整 OpenAPI 全量路由实现
- JWT/OIDC 认证提供商
- 业务包 HTTP 面
- Marketplace 商业结算 API 产品化

## 关联

- [../project/PHX-G18_ARCHITECTURE_GATE.md](../project/PHX-G18_ARCHITECTURE_GATE.md)
- [ADR-0032-release-train-boundary.md](ADR-0032-release-train-boundary.md)
