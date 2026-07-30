# PHX-G146 Role→grant Product Posture Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** API Gateway / Permission / Smart Terminal  
**规范源：** ADR-0165  
**授权：** DAL-G003 Eng Explicit Defer `3`（DAL-U007）

## 1. 门禁目标

以 **只读产品姿态面** 打开 Eng Explicit Defer `3`：命名 Foundation Role→grant 产品面；显式 `auto_grant_from_role_enabled: false`；保留 G128/G129 手工写入与 G83 evaluate-only map 为非 auto-write 相对面；Terminal 薄行展示姿态；**不**交付从角色 mint grant；包仍 `0.2.1`；Alembic 仍 `0029`。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Surface kind | Read-only product posture（thin） |
| Helper | `api/gateway/role_grant_product.py` → posture dict |
| Wire | `build_role_catalog_status()` / `GET /v1/permission/roles/status` → `role_grant_product` |
| Auto-write | `auto_grant_from_role_enabled=false`；`auto_write_routes=[]`；`/permission/role-grants` ABSENT |
| Relatives | Manual G128/G129；evaluate-only G83 |
| Fail-closed | Cap≠grant；title≠permission |
| Terminal | Thin Role→grant product row |
| Package / Alembic | Stay `0.2.1` / `0029` |
| Out | Role→grant auto-write；WebAuthn ceremony；支付清算；Brain execute；Twin authorize；新 Alembic |

## 3. Exit Criteria

1. ADR-0165 Accepted。  
2. Gate / Acceptance + helper + OpenAPI + Terminal + DAL-U007 + status sync 齐。  
3. `test_api_gateway_g146_role_grant_product_posture.py` 与相关 G136/DAL/G145 合约绿。  

见 [PHX-G146_ACCEPTANCE.md](PHX-G146_ACCEPTANCE.md)。
