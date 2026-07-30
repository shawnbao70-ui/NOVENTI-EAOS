# PHX-G163 T2 / T3 Evidence Intake & Live Capture Acceptance

**日期：** 2026-07-22  
**状态：** Fully Accepted（Foundation；docs-only）  
**归属：** Phoenix Governance / Research Track  
**退出门禁：** intake board + template；0 Complete 诚实；地板仍 T1；包 `0.2.1`；Alembic `0029`  
**授权：** DAL-G003 + DAL-G004；Usage **DAL-U034**

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0180 + Architecture Gate |
| B | `T2_T3_EVIDENCE_INTAKE.md`（NRI-T2-T3-INTAKE）+ capture template |
| C | Readiness board deepen（链入 intake；仍 0/10 Complete） |
| D | RESEARCH_INDEX / LIBRARY / G2 tip / ENG tip / PROJECT_STATUS / CHANGELOG / TASKS |
| E | Manifest G163 · DAL-U034 · `test_docs_g163_*` |

## 2. 核心不变量

- 纯文档；无 Gateway / Terminal / Kernel 代码变更（不回归并发 Eng G161/G162）  
- RP-001…010 **Current floor = T1**；**不**声称 T2/T3 Complete  
- 不 Board re-Promote；不 Eng invent；不打开 mint / 支付 / Brain / Twin  
- 无新 Alembic；包仍 `0.2.1`；head 仍 `0029_eaos_declared_roles_g90`  

## 3. 自动化证据

- 契约：`tests/contracts/test_docs_g163_t2_t3_evidence_intake.py`  
- 回归：`test_docs_g155_*` · `test_docs_g159_*` · `test_delegated_authority_ledger.py`  
- Alembic head：`0029_eaos_declared_roles_g90`

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0180（非 Board 代填 Promote） |
| Constitution Review | 通过；fail-closed 持有；无 BOOK 编辑 |
| Cross-reference Review | 通过；链入 readiness + Evidence Packs；DAL-U034 |
| Documentation Review | 通过；Index/Library/tips/status sync |
| Consistency Review | 通过；包 `0.2.1`；head `0029`；ID 避开 Eng G161/G162 |
| Gap Analysis | Live 工件仍需真人现场/租户；本切片仅准备捕获路径 |
| Second-pass Review | Fully Accepted（Foundation；docs-only） |

## 5. Explicit Defer

- Live T2/T3 artifact collection / actual floor upgrade  
- Architecture Review Board re-Promote sessions  
- External PSP / metering / arbitration deepen（Eng `4` internal path is separate）  
- Brain execute / Twin authorize  
- 新 Alembic / 包版本 bump  

## 6. 证据索引

- [PHX-G163 Architecture Gate](PHX-G163_ARCHITECTURE_GATE.md)  
- [ADR-0180](../decisions/ADR-0180-t2-t3-evidence-intake-live-capture.md)  
- [T2_T3_EVIDENCE_INTAKE.md](../research/T2_T3_EVIDENCE_INTAKE.md)  
- [LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](../research/templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md)  
- [test_docs_g163_t2_t3_evidence_intake.py](../../tests/contracts/test_docs_g163_t2_t3_evidence_intake.py)  
