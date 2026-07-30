# ADR-0182 — OpenAPI Semantic Deepen (Mount Parity vs Semantic Parity)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G164  
**归属：** API Gateway / Ops / Knowledge / AI / Event / Brain / Twin / Workflow / Smart Terminal  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U036**；cue「继续全量 OpenAPI 语义深挖」（Natural Pause resume gate）

## 背景

PHX-G148 交付只读 OpenAPI inventory posture，但 `full_openapi_http_complete=false` 与 fence `full_openapi_http_route_parity_t0188` 未区分 **route mount** 与 **semantic schema**。实测当前 14 份契约的全部 OpenAPI 操作均已挂载 `/v1` FastAPI 路由；T-0188 剩余主要是响应/错误/状态码合同诚实。PO cue「继续全量 OpenAPI 语义深挖」打开本大切片。

ID 协调：G160 WebAuthn / G161 Role→grant / G162 payment / G163 Research intake 已占用；本切片 = **PHX-G164 / ADR-0182 / DAL-U036**。

## 决策

1. Inventory helper 增加 `route_mount_parity_complete=true`；fence 重命名为 `full_openapi_semantic_parity_t0188`；`t0188_status` → `mount_parity_complete_semantic_partial`；里程碑 **PHX-G164**；`full_openapi_http_complete` **仍为 false**。  
2. 对齐高价值语义漂移（OpenAPI → 现网 Gateway，不发明行为）：  
   - Knowledge：`UuidResult` → `{id}`；`KernelError` → Gateway `detail` 信封  
   - AI / Event：`KernelError` → Gateway `detail`；AI status 文档化 fence 字段  
   - Brain/Twin：文档化 fail-closed **403** + `BRAIN_EXECUTION_FORBIDDEN` / `TWIN_EXECUTION_FORBIDDEN`；status fence 字段  
   - Workflow：status `approval_source_of_truth=workflow_kernel`  
3. `ops.openapi.yaml` → **1.0.2**；相关域 OpenAPI patch bump；Terminal 薄行同步 mount/semantic 文案。  
4. **不**打开 Brain execute / Twin authorize / Const·BP rewrite；**不**声称 100% semantic complete；**不**回归 G160–G163 产品面；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out（本切片不开口）

- `full_openapi_http_complete=true` / 全量跨域语义统一  
- Brain execute enable；Twin authorize enable  
- WebAuthn attestation crypto；Cap→grant；external PSP  
- 跨域 UuidResult 方言统一为单一形状（仅修正 Knowledge 漂移）  
- 新 Alembic；包版本 bump  

## 后果

- T-0188 记录为 **部分完成加深（mount parity 完成；semantic 仍部分）**。  
- Natural Pause 的「Full OpenAPI semantic deepen」resume gate 已行使；其余 HARD HOLDS 仍关闭。

## 关联

- [../project/PHX-G164_ARCHITECTURE_GATE.md](../project/PHX-G164_ARCHITECTURE_GATE.md)  
- [../project/PHX-G164_ACCEPTANCE.md](../project/PHX-G164_ACCEPTANCE.md)  
- [ADR-0167-openapi-inventory-product-posture.md](ADR-0167-openapi-inventory-product-posture.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
