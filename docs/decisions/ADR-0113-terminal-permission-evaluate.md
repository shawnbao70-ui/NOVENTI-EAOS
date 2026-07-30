# ADR-0113 — Terminal Permission Evaluate Thin Probe

**状态：** Accepted  
**日期：** 2026-07-20  
**里程碑：** PHX-G94  
**归属：** Smart Terminal / Permission

## 背景

G83/G93 已交付 role grant map evaluate 与状态探针。运维仍缺 Terminal 内对 `POST /v1/permission/evaluations` 的薄调用面，以核对 `MATCHED_CONTEXT_ROLE` / grant 结果。

## 决策

1. Terminal Admin 增加 Evaluate permission 薄控件（`resource_type` / `action` / 可选 `resource_id`）。  
2. 仅调用既有 `/v1/permission/evaluations`；principal 取受信上下文 subject。  
3. 可选「Explain last decision」调用既有 `/v1/permission/decisions/{id}/explanation`。  
4. 不创建/修改 grant 或 policy；不升版本；不新增 Alembic。

## Explicit Defer

- Marketplace 支付清算 / 外部仲裁（另批）  
- 自动写 grant / Role→Policy 绑定  
- WebAuthn 注册产品页  

## 关联

- [ADR-0102-permission-role-grant-map.md](ADR-0102-permission-role-grant-map.md)
- [ADR-0112-permission-roles-status.md](ADR-0112-permission-roles-status.md)
- [../project/PHX-G94_ARCHITECTURE_GATE.md](../project/PHX-G94_ARCHITECTURE_GATE.md)
