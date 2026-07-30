# ADR-0243 — OpenAPI Named Success Envelopes Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G224  
**归属：** OpenAPI Inventory / Knowledge / Event / Package  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U097**；PO cue「充分授权…自主开发…加快」

## 背景

G200 要求成功响应具备 schema，但仍允许 path-inline object。五处 list 成功体
（knowledge entities/search/provenance、event dead-letters、package surfaces）
仍为 inline，未提升为可复用 named `$ref` envelope。

## 决策

1. 提升五处 inline 200 schema 为 named components，path 改为 `$ref`。  
2. knowledge **1.0.7**；event **1.0.7**；package **1.0.8**。  
3. Inventory `milestone=PHX-G224`；
   `t0188_status=mount_parity_complete_named_success_envelopes_honest`；ops **1.0.38**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Handler invent / runtime behavior change  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G224_ARCHITECTURE_GATE.md](../project/PHX-G224_ARCHITECTURE_GATE.md)  
