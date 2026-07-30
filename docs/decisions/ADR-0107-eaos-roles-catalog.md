# ADR-0107 — Opt-in EAOS Roles Catalog Gate

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G88  
**归属：** Platform API Gateway / Permission

## 背景

G81–G83 已有 claim→roles mint、context 承载与 opt-in evaluate map，但仍无统一只读角色目录；自动写 grant / Role 表另批。

## 决策

1. 可选 `EAOS_ROLE_CATALOG`：逗号分隔声明角色名（可与 map 独立存在）。  
2. `GET /v1/permission/roles`（租户面受信上下文）聚合：  
   - `catalog`：声明目录  
   - `oidc_map`：`EAOS_OIDC_ROLE_MAP` 目标角色  
   - `grant_map`：`EAOS_PERMISSION_ROLE_GRANT_MAP` 键，并附 `grants[]`  
3. 全空 → `enabled=false` + `roles=[]`；**永不写** DB grants。  
4. 无 Alembic；包版本仍 `0.2.0`。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- Role SQL 表 / 自动写 grant（声明角色 SQL store 见 ADR-0109 / PHX-G90；自动写 grant 仍另批）  
- MFA 注册 / WebAuthn UX  

## 关联

- [ADR-0100-oidc-claim-role-mint.md](ADR-0100-oidc-claim-role-mint.md)
- [ADR-0102-permission-role-grant-map.md](ADR-0102-permission-role-grant-map.md)
- [../project/PHX-G88_ARCHITECTURE_GATE.md](../project/PHX-G88_ARCHITECTURE_GATE.md)
