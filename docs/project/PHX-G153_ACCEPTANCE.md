# PHX-G153 Foundation Ops / Compatibility / Checklist Hygiene Acceptance

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation；docs-only）  
**归属：** Phoenix Governance / Foundation release hygiene  
**退出门禁：** Runbook + Compatibility + Checklist 对齐 G145–G152；无产品开口；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U025**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0172 + Architecture Gate |
| B | `OPERATIONS_RUNBOOK.md` milestones + Smoke/Out-of-scope fences |
| C | `COMPATIBILITY.md` G145–G152 additive notes |
| D | `RELEASE_CHECKLIST.md` Manifest milestones + Acceptance pointers |
| E | Manifest G153 · tips/status/CHANGELOG/TASKS · DAL-U025 · `test_docs_g153_*` |

## 2. 核心不变量

- 纯文档；无 Gateway / Terminal / Kernel 代码变更  
- WebAuthn：ceremony stub 503 可观测；live mint 仍 Held  
- Role→grant mint / 支付清算 / Brain execute / Twin authorize 仍 closed  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`  

## 3. 自动化证据

- 契约：`tests/contracts/test_docs_g153_foundation_ops_hygiene.py`  
- 回归：`test_docs_g152_*` · `test_release_g144.py` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0172 |
| Constitution Review | 通过；fail-closed 持有；无 BOOK 编辑 |
| Cross-reference Review | 通过；G151 stub / G152 queue 链入 Runbook/Compatibility；DAL-U025 |
| Documentation Review | 通过；三份 release 文档 + tips/status |
| Consistency Review | 通过；包 `0.2.1`；head `0029` |
| Gap Analysis | Live mint / Role→grant mint / 支付 / Board 会话仍 Held |
| Second-pass Review | Fully Accepted（Foundation；docs-only） |

## 5. Explicit Defer

- Live WebAuthn credential create/get / attestation mint  
- Role→grant auto-write / mint from role（explicit PO）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 全量 OpenAPI HTTP parity  
- 新 Alembic / 包版本 bump  

## 6. 证据索引

- [PHX-G153 Architecture Gate](PHX-G153_ARCHITECTURE_GATE.md)  
- [ADR-0172](../decisions/ADR-0172-foundation-ops-compatibility-checklist-hygiene.md)  
- [OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)  
- [COMPATIBILITY.md](../release/COMPATIBILITY.md)  
- [RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)  
- [test_docs_g153_foundation_ops_hygiene.py](../../tests/contracts/test_docs_g153_foundation_ops_hygiene.py)  
