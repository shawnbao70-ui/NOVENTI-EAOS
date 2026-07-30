# ADR-0179 — Role→grant Env-Gated Live Mint

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G161  
**归属：** API Gateway / Permission / Smart Terminal  
**授权：** **DAL-G006**（explicit PO Role→grant live mint）+ DAL-G003 + DAL-G004；Usage **DAL-U032**；AED v1.1

## 背景

PHX-G146/G156 交付了 Role→grant 只读姿态与 named stub `POST /permission/role-grants` → 503。AED HARD HOLD 要求 **live mint 需 explicit PO**。CA/PO cue「继续Role→grant live mint」满足该门槛。对称 WebAuthn env-gate 模式：默认 OFF fail-closed；显式 env 打开后走 charter-safe Role→grant（非 Cap→grant）。

## 决策

1. Env `EAOS_ROLE_GRANT_AUTO_WRITE_ENABLED`（default **false**）门控 live mint。  
2. Live mint 另需非空 `EAOS_PERMISSION_ROLE_GRANT_MAP`（G83 map）；否则 503 `GATEWAY_ROLE_GRANT_MAP_REQUIRED`。  
3. `POST /v1/permission/role-grants`：disabled → 503 `GATEWAY_ROLE_GRANT_AUTO_WRITE_DISABLED`；ready → 按 roles 展开 map，经 `Permission.grant` 写入普通 grant（G128 相对面）。  
4. 响应恒声明 `cap_is_grant=false` / `title_is_permission=false`；**永不** invent Cap→grant。  
5. Posture milestone **PHX-G161**；OpenAPI permission → **1.1.3**；Terminal 薄行同步 env 文案。  
6. 无新 Alembic；包仍 `0.2.1`。

## Explicit Out（本切片不开口）

- Marketplace 支付清算 / Eng Explicit Defer `4`  
- Brain execute / Twin authorize  
- Cap→grant invent / Capability ≠ Permission 绕过  
- 全量 OpenAPI HTTP parity（T-0188 remainder）  
- Const/BP rewrite  
- 完成 WebAuthn G160 attestation crypto（独立切片；不回归半成品）  
- 新 Alembic revision  

## 后果

- Eng `3` live mint 在 **explicit PO + env ON + map** 下可用；默认仍 503。  
- Natural Pause 的 Role→grant mint-PO resume gate 已行使；其他 invent 仍需各自门槛。

## 关联

- [../project/PHX-G161_ARCHITECTURE_GATE.md](../project/PHX-G161_ARCHITECTURE_GATE.md)  
- [../project/PHX-G161_ACCEPTANCE.md](../project/PHX-G161_ACCEPTANCE.md)  
- [ADR-0175-role-grant-auto-write-stub-deepen.md](ADR-0175-role-grant-auto-write-stub-deepen.md)  
- [ADR-0165-role-grant-product-posture.md](ADR-0165-role-grant-product-posture.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
