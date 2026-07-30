# Roadmap

**Program:** Project Phoenix  
**Product:** NOVENTI Enterprise AI Operating System (EAOS)  
**Version:** 3.0  
**Repository:** `NOVENTI-EAOS`

---

## Title

EAOS Delivery Roadmap

## Purpose

Show the constitutional delivery sequence from repository foundation to EAOS Version 2.0 under **Dual-Track Governance** (Engineering + Research).

## Scope

Platform architecture and capability milestones. Excludes Legacy ERP feature work. Research-stage capabilities remain on the NRI track until promoted.

## 当前状态

**治理：** Dual-Track Accepted（[ADR-0162](../decisions/ADR-0162-dual-track-governance.md)；[PHX-G143](PHX-G143_ACCEPTANCE.md)；[playbook](DUAL_TRACK_GOVERNANCE.md)）  
**已完成：** PHX-000 → PHX-001 → PHX-002 → PHX-003 → PHX-004 → PHX-005 → PHX-006  
**已完成治理门禁：** PHX-G01 Constitutional Convergence → PHX-G02 Smart Terminal Constitution → PHX-A03 Architecture Realignment → **PHX-G143 Dual-Track Formalization**  
**已完成 Roadmap v3 主链：** PHX-K07 → K10、P11、A12、T13、B14、E15、M16（技术）、R17  
**已完成 Post-Foundation：** PHX-G18、PHX-E19～E22、PHX-G20～G32、PHX-G34～G151、PHX-M17～M18（薄探针与 OpenAPI 目录齐；无 G33；G144 = `0.2.1` patch train；G145 = WebAuthn/MFA thin posture；G146 = Role→grant thin posture；G147 = OIDC login product surface / T-0189；G148 = OpenAPI inventory posture / T-0188 partial；**PHX-G149** = Eng soft-queue tip hygiene / `ENG_SOFT_QUEUE_TIP.md`；**PHX-G150** = AED v1.1 / `AUTONOMOUS_EXECUTION_DIRECTIVE.md`；**PHX-G151** = WebAuthn ceremony stub deepen / ADR-0170）  
**基线：** EAOS Phoenix Foundation `0.2.1`（prior `0.2.0` / PHX-R17）  
**验证：** contracts 全量绿（见 PROJECT_STATUS / CHANGELOG 当时记录）；PostgreSQL Alembic `0029`  
**下一动作（Engineering Track）：** 见 [AUTONOMOUS_EXECUTION_DIRECTIVE.md](AUTONOMOUS_EXECUTION_DIRECTIVE.md) + [ENG_SOFT_QUEUE_TIP.md](ENG_SOFT_QUEUE_TIP.md) — 最高价值选择 under HARD HOLDS；编号可选加深（Foundation harden → live WebAuthn mint；Role→grant mint 需 explicit PO）；全量 OpenAPI HTTP 路由仍延后；支付清算另批暂缓（`4`）；Eng `2` thin + **G151 stub** / `3` thin / G147–G148 / **PHX-G149** tip / **PHX-G150** AED done；多区域非目标  
**下一动作（Research Track）：** G1 peers Pass + WP Accepted（RP-001…010）；tip = [AED](AUTONOMOUS_EXECUTION_DIRECTIVE.md) + [GENERATION2_TIP_BOARD](../research/GENERATION2_TIP_BOARD.md)；**Wave 1+2+3 AR Candidates complete for RP-001…010**（[NRI-ARC-RP-001](../research/programs/RP-001-enterprise-discovery/ARCHITECTURE_REVIEW_CANDIDATE-RP-001.md)…[010](../research/programs/RP-010-future-enterprise-operating-model/ARCHITECTURE_REVIEW_CANDIDATE-RP-010.md)；DAL-U013…U022）全部 Awaiting Board；无 Board Promote 不进 Eng 队列；无自证 Board 结果；Role→grant mint closed  
**约束：** 支付网关与外部仲裁、Twin authorize、Brain execute 仍 fail-closed

## Dual-Track Delivery View

```text
Engineering Track          Research Track (NRI)
Foundation 0.2.x             RP-001…RP-010 Library
G* / ADR / Gate              Wave 1 frameworks
Explicit Defer (numbered)    Validation → Architecture Review
        \                         /
         \    Promote only?      /
          \                     /
           Blueprint → Constitution Review → Implementation
```

## Delivery Sequence

```text
PHX-000–006 Historical Foundations
        ↓
PHX-G01 Constitutional Convergence
        ↓
PHX-G02 Smart Terminal Constitution
        ↓
PHX-A03 Architecture Realignment
        ↓
PHX-K07 … K10 Complete Kernels
        ↓
PHX-P11 Platform Runtime & Event
        ↓
PHX-A12 AI Runtime & Agent
        ↓
PHX-T13 Smart Terminal
        ↓
PHX-B14 Business Packages
        ↓
PHX-E15 Enterprise Brain & Twin
        ↓
PHX-M16 Marketplace & Economy
        ↓
PHX-R17 EAOS Release Train
```

## Phase Notes

| Stage | Focus |
|-------|-------|
| Architecture | Blueprint and architecture documents inside `NOVENTI-EAOS` |
| Standards | Coding, data, API, event, AI, structure, Git |
| Kernel | Identity, Organization, Permission, Workflow, Knowledge foundations |
| Runtime | Execution, context, isolation, observability |
| Knowledge | Graph, provenance, governed retrieval |
| AI | Agents, Digital Employees, approval boundaries |
| Business Packages | Industry and domain packages on Kernel |
| Enterprise Brain | Cross-domain intelligence layer |
| Marketplace | Package economy and distribution |

## Future Expansion

Detailed milestones, dependency gates and acceptance criteria are normative in
[PHOENIX_ROADMAP_V3.md](PHOENIX_ROADMAP_V3.md).

## Related Documents

- [MASTER_PLAN.md](MASTER_PLAN.md)
- [PROJECT_STATUS.md](PROJECT_STATUS.md)
- [DUAL_TRACK_GOVERNANCE.md](DUAL_TRACK_GOVERNANCE.md)
- [PHOENIX_ROADMAP_V3.md](PHOENIX_ROADMAP_V3.md)
- [../research/RESEARCH_ROADMAP.md](../research/RESEARCH_ROADMAP.md)
- [../blueprint/BLUEPRINT_INDEX.md](../blueprint/BLUEPRINT_INDEX.md)
