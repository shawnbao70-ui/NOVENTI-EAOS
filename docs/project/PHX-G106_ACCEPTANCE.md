# PHX-G106 Workflow Signal / Cancel Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Workflow  
**退出门禁：** Terminal signal/cancel 薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓；compensate/escalate UI 另批  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0125 + Architecture Gate |
| B | Terminal Signal / Cancel workflow instance |
| C | 契约 `test_api_gateway_g106_*` |

## 2. 核心不变量

- 状态真相仍归 Workflow Kernel  
- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  
- 本切片不含 compensate/escalate  

## 3. 自动化证据

- 本地完整回归：`700 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0125 |
| Constitution Review | 通过；Kernel SoT 不变 |
| Cross-reference Review | 通过；G31/G105 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | compensate/escalate、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Terminal compensate / escalate  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G106 Architecture Gate](PHX-G106_ARCHITECTURE_GATE.md)
- [ADR-0125](../decisions/ADR-0125-workflow-signal-cancel-probe.md)
- [test_api_gateway_g106_workflow_signal_cancel.py](../../tests/contracts/test_api_gateway_g106_workflow_signal_cancel.py)
