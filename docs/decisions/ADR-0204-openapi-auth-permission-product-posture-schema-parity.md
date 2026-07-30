# ADR-0204 — OpenAPI Auth/Permission Product-Posture Schema Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G185  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U058**；PO cue「充分授权…自主开发…加快」

## 背景

G160/G161 已发出稳定的 `webauthn_product` / `role_grant_product` 字段，但 OpenAPI 仍为 `additionalProperties: true` 与宽松 required，Terminal 与客户端无法依赖契约核对 readiness 形状。

## 决策

1. Auth OpenAPI `1.3.9`：`WebauthnProductPosture` → emitted field parity（`additionalProperties: false`；`milestone` const `PHX-G160`）。  
2. Permission OpenAPI `1.1.7`：`RoleGrantProductPosture` → emitted field parity（`milestone` const `PHX-G161`）。  
3. Inventory：`milestone=PHX-G185`；`t0188_status=mount_parity_complete_auth_permission_product_posture_schemas_honest`。  
4. `full_openapi_http_complete` **仍为 false**；attestation crypto / Cap→grant / Brain / Twin / PSP 仍关闭。  
5. 包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- WebAuthn attestation crypto  
- Always-on Role→grant / WebAuthn mint  
- Full OpenAPI semantic parity  

## 关联

- [../project/PHX-G185_ARCHITECTURE_GATE.md](../project/PHX-G185_ARCHITECTURE_GATE.md)  
