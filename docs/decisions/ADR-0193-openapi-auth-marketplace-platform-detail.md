# ADR-0193 — OpenAPI Auth / Marketplace / Platform GatewayDetailError Align

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G174  
**归属：** API Gateway / OpenAPI  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U047**；PO cue「充分授权…自主开发…加快」

## 背景

G166/G170 已对齐多数域的 GatewayDetailError 与 UuidResult。Auth / platform / marketplace 的 `KernelError` 响应仍指向扁平 `ErrorResponse`/`ErrorBody`，与 FastAPI `HTTPException(detail=…)` 信封不一致。

## 决策

1. Auth / platform / marketplace OpenAPI：`responses.KernelError` → `GatewayDetailError`（`{detail:{code,message,…}}`）。  
2. Inventory：`milestone=PHX-G174`；`t0188_status=mount_parity_complete_auth_marketplace_platform_detail_aligned`。  
3. `full_openapi_http_complete` **仍为 false**（attestation crypto / PSP / 其余细语义保留）。  
4. 包仍 `0.2.1`；Alembic 仍 `0029`；不打开 HARD HOLDS。

## Explicit Out

- Claiming full OpenAPI semantic parity  
- WebAuthn attestation crypto / external PSP / Brain / Twin  

## 关联

- [../project/PHX-G174_ARCHITECTURE_GATE.md](../project/PHX-G174_ARCHITECTURE_GATE.md)  
- [ADR-0185-openapi-semantic-remainder-deepen.md](ADR-0185-openapi-semantic-remainder-deepen.md)  
- [ADR-0189-uuid-result-dialect-unification.md](ADR-0189-uuid-result-dialect-unification.md)  
