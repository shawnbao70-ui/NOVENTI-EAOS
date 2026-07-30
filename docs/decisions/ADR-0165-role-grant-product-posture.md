# ADR-0165 — Role→grant Product Posture (Thin Surface)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G146  
**归属：** API Gateway / Permission / Smart Terminal  
**授权：** DAL-G003 Eng Explicit Defer item `3`（DAL-U007）

## 背景

Eng Explicit Defer `3` 要求打开 Foundation Role→grant **产品面**。既有 G83 已交付 evaluate-only role→grant **map**（不写 grant），G128/G129 已交付手工 policy/grant 写入与 deprecate/delegate。运营面缺少显式「Role→grant 自动写入未开通」姿态。从角色自动 mint grant 的写路径仍不在本切片。

## 决策

1. 新增只读 helper `api/gateway/role_grant_product.py`，返回 Foundation Role→grant 产品姿态字典：  
   - `auto_grant_from_role_enabled: false`（常量）  
   - `auto_write_routes: []`（无 live `/permission/role-grants` 写路径）  
   - 指针：手工写入 G128/G129；evaluate-only 相对面 G83  
   - `fail_closed_reasons` 含 Cap≠grant、title≠permission，并说明 auto-write 仍关闭  
2. 将姿态挂到 `build_role_catalog_status()` → `GET /v1/permission/roles/status` 的 `role_grant_product` 字段（additive；不破坏 G93）。  
3. OpenAPI `permission.openapi.yaml` 文档化姿态字段；`info.version` patch bump。  
4. Terminal 增加薄行：展示 `auto_grant_from_role_enabled=false` + 手工/evaluate 相对面说明。  
5. **不**实现从角色插入 grant；**不**新增 Alembic；包版本保持 `0.2.1`。

## Explicit Out（本切片不开口）

- Role→grant auto-write / mint from role（`/permission/role-grants` 仍 ABSENT）  
- Live WebAuthn registration ceremony  
- Marketplace 支付清算 / 外部仲裁  
- Brain execute / Twin authorize  
- 新 Alembic revision  

## 后果

- Eng `3` 以 **thin posture surface** 满足门禁；完整 Role→grant auto-write 仍可另批。  
- Eng 下一可选加深或支付清算（`4`）仍暂缓。  
- Cap≠grant / title≠permission 宪章不变量保持；G83 evaluate-only 与 G128/G129 手工写入仍是非 auto-write 相对面。

## 关联

- [../project/PHX-G146_ARCHITECTURE_GATE.md](../project/PHX-G146_ARCHITECTURE_GATE.md)  
- [../project/PHX-G146_ACCEPTANCE.md](../project/PHX-G146_ACCEPTANCE.md)  
- [ADR-0102-permission-role-grant-map.md](ADR-0102-permission-role-grant-map.md)  
- [ADR-0147-permission-policy-grant-write-probe.md](ADR-0147-permission-policy-grant-write-probe.md)（G128–G129 Terminal write）  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
