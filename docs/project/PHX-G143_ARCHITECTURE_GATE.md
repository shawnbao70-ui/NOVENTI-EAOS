# PHX-G143 Dual-Track Governance Formalization Architecture Gate

**日期：** 2026-07-21  
**状态：** Fully Accepted（Foundation）  
**归属：** Phoenix Governance / NRI Alignment  
**规范源：** ADR-0162  
**人工确认：** Product Owner approved Dual-Track Architecture Decision Report; Chief Architect delegated to execute docs/sequencing  

## 1. 门禁目标

将 Dual-Track Governance 从架构裁决落实为 Phoenix 规范性治理资产，并与既有 NRI Charter / Promotion Rules 对齐；**不**改 Constitution、Blueprint、Kernel、Runtime。

## 2. 架构裁决

| 决策项 | 裁决 |
|--------|------|
| Strategy | Dual-Track：Engineering + Research (NRI) |
| Bridge | NRI Promotion Rules only |
| Playbook | `DUAL_TRACK_GOVERNANCE.md` |
| Code / Alembic / package | 无变更；基线仍 `0.2.0` / `0029` |
| Out | 支付清算；Role→grant；WebAuthn；`0.2.1`；多区域 SaaS；任何 fail-closed 开口 |

## 3. Exit Criteria

1. ADR-0162 Accepted。  
2. Playbook + Gate/Acceptance + MASTER_PLAN / ROADMAP / PROJECT_STATUS / NRI 交叉引用齐。  
3. `test_api_gateway_g143_*`（或等价 contracts）绿；全量 contracts 绿。  

见 [PHX-G143_ACCEPTANCE.md](PHX-G143_ACCEPTANCE.md)。
