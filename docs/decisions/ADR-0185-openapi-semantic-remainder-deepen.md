# ADR-0185 — OpenAPI Semantic Remainder Deepen (T-0188)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G166  
**归属：** API Gateway / Ops / Identity / Organization / Permission / Package / Terminal / Workflow  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U039**；PO cue「充分授权…自主开发…加快」

## 背景

PHX-G164 完成 mount parity 与高价值域（knowledge/ai/event/brain）语义对齐，但 identity/organization/permission/package/terminal/workflow 仍存在错误信封漂移（ProblemDetails / 裸 ErrorBody / ErrorResponse vs 现网 FastAPI `{"detail":{code,message}}`）。`full_openapi_http_complete` 必须保持 false。

## 决策

1. Inventory milestone → **PHX-G166**；`t0188_status` → `mount_parity_complete_semantic_remainder_deepened`；`full_openapi_http_complete=false`；fence 仍 `full_openapi_semantic_parity_t0188`。  
2. 对齐现网 Gateway 错误信封为 **GatewayDetailError**（`application/json` + `detail`）：identity / organization / permission / package / terminal / workflow。  
3. 诚实记录 UuidResult 方言：`{id}`（identity/permission/knowledge/workflow/org）与 `{data}`（package/terminal/marketplace 等）并存；**本切片不强制统一**（避免破坏性序列化改写）。  
4. ops OpenAPI → **1.0.3**；相关域 patch bump；Terminal 库存文案同步。  
5. **不**打开 Brain execute / Twin authorize / Cap→grant / external PSP / Const·BP；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out

- `full_openapi_http_complete=true`  
- 跨域 UuidResult 强制统一为单一形状  
- WebAuthn attestation crypto；Brain/Twin enable  

## 后果

- T-0188 加深为「mount complete + semantic remainder deepened」；全量 semantic parity 仍 defer。

## 关联

- [../project/PHX-G166_ARCHITECTURE_GATE.md](../project/PHX-G166_ARCHITECTURE_GATE.md)  
- [ADR-0182-openapi-semantic-deepen.md](ADR-0182-openapi-semantic-deepen.md)  
