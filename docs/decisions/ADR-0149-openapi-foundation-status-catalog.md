# ADR-0149 — OpenAPI Foundation Status Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G130  
**归属：** API Contracts / Foundation Observability

## 背景

Gateway 已交付多域 `GET */status` 只读姿态探针，但 `docs/api/*.openapi.yaml` 未收录这些路径（仅 Organization unit lifecycle `PUT .../status` 存在）。契约目录与运行时漂移。

## 决策

1. 在既有 9 份域 OpenAPI 中补齐 Foundation status GET：  
   identity / organization / permission(roles) / workflow / knowledge / packages / twin / brain / ai / marketplace。  
2. 通用响应用 `FoundationStatusEnvelope`（`writable` + `supported_surfaces`；允许附加 fail-closed 字段）。  
3. Roles status 用专用 `RoleCatalogStatusEnvelope`（G93 脱敏摘要）。  
4. Auth 三件套（`/auth/oidc|idp|jwt/status`）另批（需新建 `auth.openapi.yaml`）。  
5. 无运行时改动；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- `auth.openapi.yaml` + OIDC/IdP/JWT status  
- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- WebAuthn 注册产品页  
- Foundation `0.2.1` 发布列车  

## 关联

- [../project/PHX-G130_ARCHITECTURE_GATE.md](../project/PHX-G130_ARCHITECTURE_GATE.md)
