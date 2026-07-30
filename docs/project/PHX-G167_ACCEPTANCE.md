# PHX-G167 Demo Bootstrap Context Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Demo Gateway / Smart Terminal  
**退出门禁：** demo-only bootstrap；生产未挂载；无 secrets；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U040**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0186 + Architecture Gate |
| B | `GET /v1/demo/bootstrap` on demo app only |
| C | Terminal auto-fill Subject/Tenant on boot |
| D | tip/status/Manifest/DAL-U040 |
| E | `test_api_gateway_g167_*` |

## 2. 核心不变量

- 生产 `api.gateway.app` 不挂载 `/v1/demo/*`  
- 响应不含 secret/token  
- 不打开 HARD HOLDS  

## 3. 自动化证据

- `tests/contracts/test_api_gateway_g167_demo_bootstrap.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0186 |
| Constitution Review | 通过；dev-only；无 BOOK 编辑 |
| Cross-reference Review | 通过；DAL-U040 |
| Documentation Review | 通过 |
| Consistency Review | 通过；`0.2.1` / `0029` |
| Gap Analysis | Marketplace-signed extension UI 仍 defer |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Marketplace-signed extension UI  
- Production demo surface（永不）  
- Brain execute / Twin authorize  

## 6. 证据索引

- [PHX-G167 Architecture Gate](PHX-G167_ARCHITECTURE_GATE.md)  
- [ADR-0186](../decisions/ADR-0186-demo-bootstrap-context.md)  
- [demo_bootstrap.py](../../api/gateway/routers/demo_bootstrap.py)  
