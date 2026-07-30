# PHX-G109 Package Publish / Install / Disable / Resolve Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package  
**退出门禁：** Terminal publish/install/disable/resolve 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0128 + Architecture Gate |
| B | Terminal 四控件 |
| C | 契约 `test_api_gateway_g109_*` |

## 2. 核心不变量

- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  

## 3. 自动化证据

- 本地完整回归：`706 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0128 |
| Constitution Review | 通过；Gateway 薄适配 |
| Cross-reference Review | 通过；G27/G108 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | Knowledge Terminal、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Knowledge Terminal 薄探针  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G109 Architecture Gate](PHX-G109_ARCHITECTURE_GATE.md)
- [ADR-0128](../decisions/ADR-0128-package-publish-install-resolve-probe.md)
- [test_api_gateway_g109_package_lifecycle.py](../../tests/contracts/test_api_gateway_g109_package_lifecycle.py)
