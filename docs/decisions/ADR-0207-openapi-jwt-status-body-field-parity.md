# ADR-0207 — OpenAPI JWT Status Body Field Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G188  
**归属：** API Gateway / Auth / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U061**；PO cue「充分授权…自主开发…加快」

## 背景

`GET /auth/jwt/status` 已发出稳定的 JWT/denylist 形状，但 OpenAPI 仍复用宽松
`AuthStatusEnvelope`，无法契约核对 denylist 计数与 flags。

## 决策

1. Auth OpenAPI **1.3.11**：新增 `JwtStatusEnvelope` / `JwtStatusData` /
   `JwtDenylistPosture`（emitted field parity；永不列出 jti）。  
2. `GET /auth/jwt/status` 200 → `JwtStatusEnvelope`。  
3. Inventory：`milestone=PHX-G188`；
   `t0188_status=mount_parity_complete_jwt_status_body_field_parity`。  
4. Ops OpenAPI **1.0.15** 同步 inventory const。  
5. `full_openapi_http_complete` **仍为 false**；IdP aggregation 全量 schema 仍后置；
   attestation crypto / Brain / Twin / PSP / Cap→grant 仍关闭。  
6. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- IdP status full nested schema invent  
- Denylist jti dump  
- Full OpenAPI semantic parity  

## 关联

- [../project/PHX-G188_ARCHITECTURE_GATE.md](../project/PHX-G188_ARCHITECTURE_GATE.md)  
