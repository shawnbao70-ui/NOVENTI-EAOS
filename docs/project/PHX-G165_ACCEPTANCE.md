# PHX-G165 Terminal Declared Package Surface Projection Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Package Platform / Demo Gateway  
**退出门禁：** Product/Ops 投影声明式 surfaces；resolve → Operator handoff；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U038**；cue「你决定，我要完整的强大的系统」

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0184 + Architecture Gate |
| B | `packages/sample_product` + demo seed install ops/product |
| C | Terminal Product/Ops load `/v1/packages/surfaces` + resolve handoff |
| D | PROJECT_STATUS / ENG tip / Manifest / DAL-U038 |
| E | `test_api_gateway_g165_declared_package_surface.py` |

## 2. 核心不变量

- Terminal 不宿主业务真相；Commit 仅经 Operator  
- 优先声明式 surfaces；fixture 仅 offline 回退  
- 不打开 Brain execute / Twin authorize / Cap→grant / external PSP  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`

## 3. 自动化证据

- 契约：`tests/contracts/test_api_gateway_g165_declared_package_surface.py`  
- 样例包：`packages/sample_ops` · `packages/sample_product`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0184 |
| Constitution Review | 通过；对齐 BOOK23 §10.1；无 BOOK 编辑 |
| Cross-reference Review | 通过；DAL-U038；tip/status sync |
| Documentation Review | 通过；Gate/Acceptance/ADR |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Marketplace 签名扩展 UI 仍未接入；semantic OpenAPI remainder 另轨 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer / Remaining Gaps

- Marketplace-signed extension UI sandbox  
- Full OpenAPI semantic parity remainder（T-0188）  
- WebAuthn attestation crypto / external PSP  
- Brain execute / Twin authorize  

## 6. 证据索引

- [PHX-G165 Architecture Gate](PHX-G165_ARCHITECTURE_GATE.md)  
- [ADR-0184](../decisions/ADR-0184-terminal-declared-package-surface-projection.md)  
- [sample_product/manifest.json](../../packages/sample_product/manifest.json)  
- [test_api_gateway_g165_declared_package_surface.py](../../tests/contracts/test_api_gateway_g165_declared_package_surface.py)  
