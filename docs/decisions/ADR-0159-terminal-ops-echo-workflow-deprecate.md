# ADR-0159 — Terminal Ops Echo + Workflow Definition Deprecation

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G140  
**归属：** Smart Terminal / Gateway ops / Workflow

## 背景

G139 已将 `/v1/context/echo` 纳入 Ops OpenAPI；Terminal 仅有 GET `/context`。Workflow OpenAPI/Gateway 已有 `POST …/definitions/{id}/deprecation`，但 Terminal 未接线。

## 决策

1. Terminal Admin 增加 Context echo 探针：故意提交 elevation 字段，期望 **400**。  
2. Terminal Admin 增加 Deprecate workflow definition，调用既有 Gateway 路径；body 对齐 OpenAPI `reason` + `expected_version`（Kernel 可忽略多余字段）。  
3. 无新 Alembic；包 `0.2.0`；≠ Role→grant / WebAuthn / 支付清算。

## Explicit Defer

- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Marketplace 支付清算 / 外部仲裁  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0158-gateway-ops-openapi-catalog.md](ADR-0158-gateway-ops-openapi-catalog.md)
- [../project/PHX-G140_ARCHITECTURE_GATE.md](../project/PHX-G140_ARCHITECTURE_GATE.md)
