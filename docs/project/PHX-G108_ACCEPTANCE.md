# PHX-G108 Package Status / Manifest / Surfaces Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package  
**退出门禁：** Terminal Package 状态/manifest/surfaces 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓；publish/install UI 另批  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0127 + Architecture Gate |
| B | `GET /v1/packages/status` + Terminal 四控件 |
| C | 契约 `test_api_gateway_g108_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  
- 本切片不含 publish/install/disable/resolve  

## 3. 自动化证据

- 本地完整回归：`704 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0127 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G27/G107 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | publish/install、Knowledge Terminal、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Terminal publish / install / disable / resolve  
- Knowledge Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G108 Architecture Gate](PHX-G108_ARCHITECTURE_GATE.md)
- [ADR-0127](../decisions/ADR-0127-package-status-manifest-surfaces-probe.md)
- [test_api_gateway_g108_package_probe.py](../../tests/contracts/test_api_gateway_g108_package_probe.py)
