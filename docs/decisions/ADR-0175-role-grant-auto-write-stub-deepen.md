# ADR-0175 — Role→grant Auto-Write Stub Deepen

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G156  
**归属：** API Gateway / Permission / Smart Terminal  
**授权：** DAL-G003 + DAL-G004 Eng Explicit Defer `3` deepen（DAL-U028）；AED v1.1

## 背景

PHX-G146 已交付只读 Role→grant 产品姿态（`auto_grant_from_role_enabled=false`；`auto_write_routes=[]`）。AED 允许 Eng `3` **deepen**（非 mint）：对称 G151 WebAuthn，命名 auto-write stub 并以 503 fail-closed 固定边界。**Live mint 仍需 explicit PO**（HARD HOLD / Explicit Defer 规则）。

## 决策

1. 新增 stub helper `api/gateway/role_grant_auto_write.py`：统一 503 + `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`；detail 含 `auto_write_step` / `grant_minted=false` / Cap≠grant / title≠permission / `next_action=none`。  
2. 新增 FastAPI 路由 `api/gateway/routers/role_grants.py`：`POST /v1/permission/role-grants` → 503。  
3. 更新 `role_grant_product`：`auto_write_routes` 列出 stub；里程碑 **PHX-G156**；`auto_write_stub_observability=true`；enabled 仍恒 `false`。  
4. OpenAPI `permission.openapi.yaml` → **1.1.2**；去掉 `auto_write_routes` 的 `maxItems: 0`。  
5. Terminal 薄行同步 stub 503 文案。  
6. **不**从角色插入 grant；**不**把本切片当作 mint 授权；**不**新增 Alembic；包仍 `0.2.1`。

## Explicit Out（本切片不开口）

- Role→grant live auto-write / mint from role（仍需 **explicit PO**）  
- Live WebAuthn credential mint  
- Marketplace 支付清算 / 外部仲裁（Eng `4`）  
- Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- Eng `3` 以 **named stub 503** 加深；mint 仍另批且需 PO。  
- G83 evaluate-only 与 G128/G129 手工写入仍是非 auto-write 相对面。

## 关联

- [../project/PHX-G156_ARCHITECTURE_GATE.md](../project/PHX-G156_ARCHITECTURE_GATE.md)  
- [../project/PHX-G156_ACCEPTANCE.md](../project/PHX-G156_ACCEPTANCE.md)  
- [ADR-0165-role-grant-product-posture.md](ADR-0165-role-grant-product-posture.md)  
- [ADR-0170-webauthn-ceremony-stub-deepen.md](ADR-0170-webauthn-ceremony-stub-deepen.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
