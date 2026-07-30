# ADR-0215 — OpenAPI RoleGrant Auto-Write Response/Detail Parity

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G196  
**归属：** Permission OpenAPI / Inventory  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U069**；PO cue「充分授权…自主开发…加快」

## 背景

G185/G195 已对齐 Role→grant product posture 与 RoleCatalogStatus，但
`POST /permission/role-grants` 的 200/503 body 仍 `additionalProperties: true`，
与 `role_grant_auto_write.py` emit 不一致。

## 决策

1. Permission OpenAPI **1.1.9**：  
   - `RoleGrantAutoWriteMintResponse` field parity（含 `RoleGrantMintedGrant`）  
   - `RoleGrantAutoWriteStubDetail` field parity（`next_action` enum；`milestone` const PHX-G161）  
2. Inventory：`milestone=PHX-G196`；
   `t0188_status=mount_parity_complete_role_grant_auto_write_response_detail_parity`；
   ops **1.0.22**。  
3. Default auto-write 仍 fail-closed；不打开 Cap→grant / always-on mint。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Cap→grant invent  
- Always-on Role→grant mint without env  
- HARD HOLD openings  

## 关联

- [../project/PHX-G196_ARCHITECTURE_GATE.md](../project/PHX-G196_ARCHITECTURE_GATE.md)  
