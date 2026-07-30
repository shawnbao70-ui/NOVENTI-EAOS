# ADR-0180 — T2 / T3 Evidence Intake & Live Capture Board

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G163  
**归属：** Phoenix Governance / Research Track  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U034**

## 背景

PHX-G155 固定了 RP-001…010 证据地板为 **T1** 与诚实 T2/T3 criteria；PHX-G159 Board Hold×10 以 T1 诚实为由 Hold。Natural Pause / Eng tip 将 **live T2/T3** 列为 resume gate。CA/PO cue「继续Live T2/T3 证据升档」要求升档路径，但仓库内 **无** 真人现场/租户 live 工件。伪造 Complete 或静默升档违反 Charter。

并发 Eng 已占用 PHX-G161（Role→grant mint；ADR-0179）与 PHX-G162（payment；ADR-0181）；Research 使用 **PHX-G163 / ADR-0180 / DAL-U034** 避免碰撞。

## 决策

1. 新增 docs-only intake board：`docs/research/T2_T3_EVIDENCE_INTAKE.md`（**NRI-T2-T3-INTAKE**）。  
2. 新增 capture template：`docs/research/templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md`（**NRI-TPL-LIVE-EVID**）。  
3. 明确 T2 vs T3 intake bars、intake checklist、verification checklist、Live Capture Registry；**0 / 10 Complete** 诚实声明。  
4. **不**将任何 RP Current floor 升至 T2/T3；**不** invent live artifacts。  
5. 深化 [T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md) 链入 intake；里程碑 **PHX-G163**。  
6. Docs-only Fully Accepted；包 **`0.2.1`**；Alembic **`0029`**。

## Explicit Out（本切片不开口）

- Fake T2/T3 Complete / 静默地板升档  
- Board re-Promote / Eng invent from Research  
- Live WebAuthn mint / Role→grant mint / 支付清算（Eng 另切片）  
- Brain execute / Twin authorize / Const/BP rewrite  
- 新 Alembic / 包版本 bump  

## 后果

- Research tip 具备可执行的 live 捕获路径，而不假装已有 live 证据。  
- 下一「继续」仅在真实工件到达后才可做 floor flip。

## 关联

- [../research/T2_T3_EVIDENCE_INTAKE.md](../research/T2_T3_EVIDENCE_INTAKE.md)  
- [../research/T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md)  
- [../research/templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md](../research/templates/LIVE_EVIDENCE_CAPTURE_TEMPLATE.md)  
- [../project/PHX-G163_ARCHITECTURE_GATE.md](../project/PHX-G163_ARCHITECTURE_GATE.md)  
- [../project/PHX-G163_ACCEPTANCE.md](../project/PHX-G163_ACCEPTANCE.md)  
- [ADR-0174-t2-t3-evidence-readiness-board.md](ADR-0174-t2-t3-evidence-readiness-board.md)  
- [ADR-0178-generation1-architecture-review-board-hold.md](ADR-0178-generation1-architecture-review-board-hold.md)  
