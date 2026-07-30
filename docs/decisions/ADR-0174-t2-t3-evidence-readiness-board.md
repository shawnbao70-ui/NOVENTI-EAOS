# ADR-0174 — T2 / T3 Evidence Readiness Board

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G155  
**归属：** Phoenix Governance / Research Track  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U027**

## 背景

Generation-1（RP-001…010）Peer Pass + WP content Accepted，且 Architecture Review Candidate Packages 已全部打开（Awaiting Board）。AED Research 默认输出在 AR Candidates 之后指向 **T2/T3 evidence**，但缺少单一 standing board 固定：**当前地板仍是 T1**、**何为诚实 T2/T3**、**禁止纸面升档**。

## 决策

1. 新增 docs-only standing board：`docs/research/T2_T3_EVIDENCE_READINESS.md`（**NRI-T2-T3-EVID**）。  
2. 明确 RP-001…010 **Current floor = T1**；**0 / 10** live T2/T3 Complete。  
3. 仅记载 Planned readiness bars 与注册流程；**不** invent live plant/executive evidence。  
4. PHX-G155 为 **docs-only** Fully Accepted；无 Gateway/Kernel 代码、无新 Alembic、包版本保持 **`0.2.1`**、Alembic head 保持 **`0029`**。  
5. **不**自证 AR Board、不 Eng invent、不打开 Brain execute / Twin authorize / live WebAuthn mint / Role→grant mint / Eng `4`。

## Explicit Out（本切片不开口）

- 将任何 RP 标为 T2/T3 Complete（无 live 工件）  
- Architecture Review Board self-certify / 代填 decision  
- Eng soft-queue invent from Research  
- Live WebAuthn mint / Role→grant mint / 支付清算  
- Brain execute / Twin authorize / Const/BP rewrite  
- 新 Alembic / 包版本 bump  

## 后果

- Board 与 Dual-Track 可同时看 AR queue（调度）与 T2/T3 readiness（证据诚实度）。  
- 下一「继续」不得伪称 live evidence。

## 关联

- [../research/T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md)  
- [../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)  
- [../project/PHX-G155_ARCHITECTURE_GATE.md](../project/PHX-G155_ARCHITECTURE_GATE.md)  
- [../project/PHX-G155_ACCEPTANCE.md](../project/PHX-G155_ACCEPTANCE.md)  
- [ADR-0169-autonomous-execution-directive.md](ADR-0169-autonomous-execution-directive.md)  
- [ADR-0171-architecture-review-board-queue-and-release-hygiene.md](ADR-0171-architecture-review-board-queue-and-release-hygiene.md)  
