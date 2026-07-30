# PHX-G164 OpenAPI Semantic Deepen Architecture Gate

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Ops / Domain OpenAPI / Smart Terminal  
**规范源：** ADR-0182  
**授权：** DAL-G003 + DAL-G004（DAL-U036）；AED v1.1；cue「继续全量 OpenAPI 语义深挖」

## 1. 门禁目标

在不发明新域、不打开 HARD HOLDS 的前提下，诚实区分 **route mount parity** 与 **semantic parity**，并对齐最高价值 OpenAPI↔Gateway 语义漂移；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Inventory | `route_mount_parity_complete=true`；`full_openapi_http_complete=false` |
| Fence | `full_openapi_semantic_parity_t0188`（取代 route_parity 命名） |
| t0188_status | `mount_parity_complete_semantic_partial` |
| Knowledge | UuidResult `{id}` + GatewayDetailError |
| AI / Event | GatewayDetailError；AI status fences |
| Brain / Twin | Document 403 fail-closed；status fences；**不** enable execute/authorize |
| Workflow | `approval_source_of_truth` documented |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Full semantic claim；Brain/Twin enable；Const/BP；G160–G163 regress |

## 3. Exit Criteria

1. ADR-0182 Accepted。  
2. Gate / Acceptance + helper/OpenAPI/Terminal + DAL-U036 + tip/status sync 齐。  
3. `test_api_gateway_g164_*` 与软化后的 G148 / ops OpenAPI 合约绿。  

见 [PHX-G164_ACCEPTANCE.md](PHX-G164_ACCEPTANCE.md)。
