# PHX-G104 Workflow Status / Definition / Instance Thin Probe Acceptance

**日期：** 2026-07-20  
**状态：** Fully Accepted（Foundation）  
**归属：** Smart Terminal / Workflow  
**退出门禁：** Terminal Workflow 状态/定义/实例/任务薄探针；包 `0.2.0`；Alembic `0029`  
**人工确认：** Marketplace 支付清算另批暂缓；审批写路径 UI 另批  

## 1. 交付范围

| 切片 | 交付 |
|------|------|
| A | ADR-0123 + Architecture Gate |
| B | `GET /v1/workflow/status` + Terminal 五控件 |
| C | 契约 `test_api_gateway_g104_*` |

## 2. 核心不变量

- 审批真相仍归 Workflow Kernel  
- 禁止 body 上下文提升  
- 不新增 Alembic / 不升版本  
- 本切片不含 Terminal approve/reject/signal  

## 3. 自动化证据

- 本地完整回归：`696 passed`（`tests/contracts`）  
- Alembic head：`0029_eaos_declared_roles_g90`  

## 4. 七步自审

| 审查 | 结论 |
|------|------|
| Architecture Review | 通过；ADR-0123 |
| Constitution Review | 通过；审批 SoT 不变 |
| Cross-reference Review | 通过；G23/G103 仍绿 |
| Documentation Review | 通过 |
| Consistency Review | 通过；包 `0.2.0`；head `0029` |
| Gap Analysis | 审批写路径 UI、支付清算、WebAuthn、Role→grant 另批 |
| Second-pass Review | Fully Accepted（Foundation） |

## 5. Explicit Defer

- Terminal 任务审批 / 信号 / 取消 / 补偿 / 升级  
- Marketplace 支付清算 / 外部仲裁（另批，已确认）  
- 自动写 grant / Role→Policy  
- WebAuthn 注册产品页  

## 6. 证据索引

- [PHX-G104 Architecture Gate](PHX-G104_ARCHITECTURE_GATE.md)
- [ADR-0123](../decisions/ADR-0123-workflow-status-definition-instance-probe.md)
- [test_api_gateway_g104_workflow_probe.py](../../tests/contracts/test_api_gateway_g104_workflow_probe.py)
