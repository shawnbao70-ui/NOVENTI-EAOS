# ADR-0249 — OpenAPI Federation Matrix Payload Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G230  
**归属：** OpenAPI Inventory / Platform / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U103**；PO cue「充分授权…自主开发…加快」

## 背景

`FederationMatrixEnvelope.data` 仍为 nested anonymous；`meta` 为 opaque
`additionalProperties: true`，与 live emit 六键漂移。Auth
`IdpFederationStatusPosture.matrix` 亦为嵌套匿名摘要。

## 决策

1. 新增 `FederationMatrixCell` / `FederationMatrixPayload` / `FederationMatrixMeta`。  
2. Auth 新增 `IdpFederationMatrixSummary`；matrix → `$ref`。  
3. platform **1.0.7**；auth **1.3.20**。  
4. Inventory `milestone=PHX-G230`；
   `t0188_status=mount_parity_complete_federation_matrix_payload_named_honest`；ops **1.0.41**。  
5. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Federation invent / IdP behavior change  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G230_ARCHITECTURE_GATE.md](../project/PHX-G230_ARCHITECTURE_GATE.md)  
