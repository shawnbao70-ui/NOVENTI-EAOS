# PHX-G148 OpenAPI Inventory Product Posture Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Ops / Smart Terminal  
**规范源：** ADR-0167  
**授权：** DAL-G003（DAL-U009）；T-0188 部分完成（inventory posture；全量路由仍延后）

## 1. 门禁目标

以 **只读 OpenAPI 库存产品姿态** 部分回应 T-0188「全量 OpenAPI HTTP 路由实现延后」：命名 contract count、adapter registry 对齐、thin-probe 域 vs 尚无探针域、known defer fences；**不**交付全量 FastAPI 路由；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Read-only inventory product posture（thin） |
| Helper | `api/gateway/openapi_inventory_product.py` → posture dict |
| Wire | `GET /v1/adapters` → `meta.openapi_inventory_product`（additive） |
| Sources | `list_openapi_contracts()` + `list_adapters()` + known thin-probe / defer fences |
| Full surface claim | `full_openapi_http_complete=false` |
| Terminal | Optional thin row（contract count + 全量路由仍延后） |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | 全量 HTTP 路由；新 `/v1/openapi/inventory`；支付清算；Brain execute；Twin authorize；WebAuthn ceremony；Role→grant mint；新 Alembic |

## 3. Exit Criteria

1. ADR-0167 Accepted。  
2. Gate / Acceptance + helper + ops OpenAPI + DAL-U009 + status sync 齐；T-0188 标为部分完成。  
3. `test_api_gateway_g148_openapi_inventory_product.py` 与 `test_release_r17` / DAL 合约绿。  

见 [PHX-G148_ACCEPTANCE.md](PHX-G148_ACCEPTANCE.md)。
