# ADR-0161 — Organization Get Enterprise Thin Probe

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G142  
**归属：** Smart Terminal / Organization

## 背景

Gateway 已有 `GET /v1/enterprises/{enterprise_id}`（G32/OpenAPI）。Terminal 覆盖 Create/List 与 lifecycle，但缺 Get。

## 决策

1. Terminal Admin 增加 Get enterprise，调用既有 GET 路径。  
2. 使用 `orgEnterpriseId` 输入；无 body 抬升。  
3. 同步 `api/README.md` Complete Terminal UI 目录至 G140–G142。  
4. 无新 Alembic；包 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁  
- Role→grant 自动写入  
- Full WebAuthn / MFA registration product page  
- Foundation `0.2.1` 发布列车  

## 关联

- [ADR-0141-organization-status-tenant-enterprise-probe.md](ADR-0141-organization-status-tenant-enterprise-probe.md)
- [../project/PHX-G142_ARCHITECTURE_GATE.md](../project/PHX-G142_ARCHITECTURE_GATE.md)
