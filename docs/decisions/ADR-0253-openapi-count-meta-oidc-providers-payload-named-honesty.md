# ADR-0253 — OpenAPI CountMeta + OidcProvidersPayload Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G234  
**归属：** OpenAPI Inventory / Platform / Auth  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U107**；PO cue「充分授权…自主开发…加快」

## 背景

nested anonymous ≥1 残差仅余：三处 platform list `meta.count` 与 Auth
`OidcProvidersEnvelope.data.providers` 包装。

## 决策

1. 新增共享 `CountMeta`；三处 list envelope meta → `$ref`。  
2. 新增 `OidcProvidersPayload`；envelope data → `$ref`。  
3. platform **1.0.8**；auth **1.3.21**；ops **1.0.43**。  
4. Inventory `milestone=PHX-G234`；
   `t0188_status=mount_parity_complete_count_meta_and_oidc_providers_payload_named_honest`。  
5. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

HARD HOLD openings；semantic-complete claim。  
