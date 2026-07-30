# ADR-0247 — OpenAPI Nested Data Payload Named Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G228  
**归属：** OpenAPI Inventory / Event / Ops  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U101**；PO cue「充分授权…自主开发…加快」

## 背景

四处分量 ≥4 的 nested anonymous `data` object 仍内联在 named Result/Envelope 中：
DeliveryReport/DispatchReport/DeliveryStats + ReleaseEnvelope。

## 决策

1. 提升为 `DeliveryReportPayload` / `DispatchReportPayload` / `DeliveryStatsPayload` / `ReleasePosture`。  
2. event **1.0.8**；ops **1.0.40**。  
3. Inventory `milestone=PHX-G228`；
   `t0188_status=mount_parity_complete_nested_data_payload_named_honest`。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- Handler invent  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G228_ARCHITECTURE_GATE.md](../project/PHX-G228_ARCHITECTURE_GATE.md)  
