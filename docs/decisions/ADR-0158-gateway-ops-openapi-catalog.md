# ADR-0158 — Gateway Ops OpenAPI Catalog

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G139  
**归属：** API Contracts / Gateway meta

## 背景

G18 已交付 `/v1/health`、`/release`、`/adapters`、`/context`、`/context/echo`。领域 OpenAPI 在 G130–G138 补齐后，元面仍无规范性契约文件。

## 决策

1. 新增 `docs/api/ops.openapi.yaml`，收录上述五条元面路径。  
2. Release Manifest / adapters **13 → 14**。  
3. 明确 body 禁止抬升 `tenant_id` / `subject_id` / `platform_scope` / `session_id` / `roles`。  
4. 无运行时变更；包版本仍 `0.2.0`；Alembic 仍 `0029`。

## Explicit Defer

- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0154-platform-openapi-catalog.md](ADR-0154-platform-openapi-catalog.md)
- [../project/PHX-G139_ARCHITECTURE_GATE.md](../project/PHX-G139_ARCHITECTURE_GATE.md)
