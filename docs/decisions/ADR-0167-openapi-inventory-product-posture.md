# ADR-0167 — OpenAPI Inventory Product Posture (Thin)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G148  
**归属：** API Gateway / Ops / Smart Terminal  
**授权：** DAL-G003 charter-safe continuous autonomy（DAL-U009）

## 背景

T-0188 将「全量 OpenAPI HTTP 路由实现」标为延后。Manifest 已登记 14 份 OpenAPI 契约，adapter registry 对齐契约路径，各域已有薄 HTTP 探针；运营面缺少命名的 **OpenAPI Inventory Product** 只读姿态，无法在不声称全量 FastAPI 面完成的前提下说明合同计数、注册表对齐与 thin-probe / defer 分界。

## 决策

1. 新增只读 helper `api/gateway/openapi_inventory_product.py`，返回 Foundation OpenAPI 库存产品姿态：  
   - `openapi_contract_count` 来自 `list_openapi_contracts()`  
   - `adapter_registry_status` / `adapter_count` 来自 `list_adapters()` 并对齐契约路径  
   - `thin_probe_domains` 列出已挂薄 HTTP 探针的网关域  
   - `deferred_domains` 列出尚无薄探针的目录域（当前为空）  
   - `known_defer_fences` 命名全量路由与其它 fail-closed 延后栅栏  
   - `full_openapi_http_complete: false`（明确不关闭全量路由）  
2. 将姿态挂到 `GET /v1/adapters` 的 `meta.openapi_inventory_product`（additive；保留既有 `meta.count`）。  
3. OpenAPI `ops.openapi.yaml` 文档化姿态字段；`info.version` patch bump（1.0.0 → 1.0.1）。  
4. Terminal 可选薄行展示合同计数与「全量路由仍延后」。  
5. **不**实现缺失的全量 HTTP 路由；**不**新增 Alembic；包版本保持 `0.2.1`；支付清算 / Brain execute / Twin authorize / WebAuthn ceremony / Role→grant mint 仍关闭。

> **Superseding note (PHX-G164 / ADR-0182):** route **mount** parity is now complete；inventory reports `route_mount_parity_complete=true` while `full_openapi_http_complete` remains false for **semantic** remainder.
## Explicit Out（本切片不开口）

- 全量 OpenAPI → FastAPI 路由 parity（T-0188 剩余）  
- Live WebAuthn registration ceremony  
- Role→grant auto-write / mint from role  
- Marketplace 支付清算 / 外部仲裁  
- Brain execute / Twin authorize  
- 新 Alembic revision  
- 新独立 `/v1/openapi/inventory` 路由（避免 router sprawl）

## 后果

- T-0188「全量 OpenAPI HTTP 路由实现延后」以 **部分完成（inventory posture G148；全量路由仍延后）** 记录；**不**声称 Foundation FastAPI 面完整。  
- Eng 下一可选加深仍为 WebAuthn ceremony / Role→grant auto-write；支付清算（`4`）仍暂缓。

## 关联

- [../project/PHX-G148_ARCHITECTURE_GATE.md](../project/PHX-G148_ARCHITECTURE_GATE.md)  
- [../project/PHX-G148_ACCEPTANCE.md](../project/PHX-G148_ACCEPTANCE.md)  
- [ADR-0032-release-train-boundary.md](ADR-0032-release-train-boundary.md)  
- [ADR-0033-api-gateway-boundary.md](ADR-0033-api-gateway-boundary.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
