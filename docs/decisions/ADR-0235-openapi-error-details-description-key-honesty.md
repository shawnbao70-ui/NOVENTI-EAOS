# ADR-0235 — OpenAPI ErrorResponse.details Description-Key Honesty

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G216  
**归属：** OpenAPI Inventory / Organization / Permission / Platform / Workflow  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U089**；PO cue「充分授权…自主开发…加快」

## 背景

G202/G204 在 `ErrorResponse.details` 声明了 known-shape（`fields[]`）描述，
但 organization / permission / platform / workflow 四份契约在 `properties`
之后又有第二个同级 `description` 键。YAML 映射只保留后者，known-shape
文案在解析时被静默覆盖。

## 决策

1. 四处契约合并为**单一** `details.description`，保留 known-shape + live emit
   语义，并标注 G216。  
2. org **1.0.6**；permission **1.1.13**；platform **1.0.5**；workflow **1.0.8**。  
3. Inventory `milestone=PHX-G216`；
   `t0188_status=mount_parity_complete_error_details_description_key_honest`；
   ops **1.0.34**。  
4. `full_openapi_http_complete=false`；包 `0.2.1`；Alembic `0029`。

## Explicit Out

- New details fields invent  
- Semantic-complete claim  
- HARD HOLD openings  

## 关联

- [../project/PHX-G216_ARCHITECTURE_GATE.md](../project/PHX-G216_ARCHITECTURE_GATE.md)  
