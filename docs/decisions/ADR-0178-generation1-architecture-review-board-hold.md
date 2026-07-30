# ADR-0178 — Generation-1 Architecture Review Board Session (Hold)

**状态：** Accepted  
**日期：** 2026-07-22  
**里程碑：** PHX-G159  
**归属：** Phoenix Governance / Research Track Architecture Review  
**授权：** **DAL-G005**（CA-authorized Board session）+ DAL-G003 + DAL-G004；Usage **DAL-U031**

## 背景

NRI-ARC-RP-001…010 Candidate Packages were queued（PHX-G152）and evidence floors remain **T1**（PHX-G155）。Natural Pause（PHX-G158）listed Architecture Review Board as a resume gate. CA/PO cue 2026-07-22：「继续，Architecture Review Board 填 Promote/Hold/Reject」— explicit Board-session authorization（not silent self-certify）。

## 决策

1. Mint **DAL-G005**：CA-authorized Generation-1 Architecture Review Board session to record Promote / Hold / Reject on NRI-ARC-RP-001…010.  
2. Record **Board Decision — Hold** for **all ten** packages（PHX-G159）：Remain Research Asset；T1 floor；**no Eng soft-queue ingest**；no Const/BP rewrite as production truth.  
3. Update standing queue [ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md) to reflect session outcome.  
4. Eng Track Natural Pause remains for product invent；Board Hold **does not** open Eng soft-queue.  
5. Package stays **`0.2.1`**；Alembic stays **`0029`**；docs-only.

## Why Hold (not Promote / Reject)

| Factor | Assessment |
|--------|------------|
| Evidence floor | All RP-001…010 remain **T1**；0 live T2/T3 Complete |
| Promotion Rules | Promote requires Board + sufficient maturity；T1 honesty → Hold |
| Eng readiness | No Phoenix ADR ingest path opened；Hold ≠ Eng invent |
| Reject | Packages are coherent Research Assets；not defective — Hold, not Reject |

## Explicit Out（本切片不开口）

- Promote / Eng soft-queue invent from Research  
- Live WebAuthn mint / Role→grant live mint  
- Eng `4` 支付清算  
- Brain execute / Twin authorize  
- Const/BP rewrite as production truth  
- Fake T2/T3 tier upgrade  

## 后果

- Board decision blocks filled under DAL-G005；queue Status = Hold.  
- Revisit after live T2/T3 per [T2_T3_EVIDENCE_READINESS.md](../research/T2_T3_EVIDENCE_READINESS.md).  
- Next Research tip: remain Research Asset；no Eng ingest from Hold.

## 关联

- [../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)  
- [../project/PHX-G159_ARCHITECTURE_GATE.md](../project/PHX-G159_ARCHITECTURE_GATE.md)  
- [../project/PHX-G159_ACCEPTANCE.md](../project/PHX-G159_ACCEPTANCE.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)（DAL-G005 / DAL-U031）  
- [ADR-0171-architecture-review-board-queue-and-release-hygiene.md](ADR-0171-architecture-review-board-queue-and-release-hygiene.md)  
- [ADR-0177-autonomous-soft-queue-natural-pause.md](ADR-0177-autonomous-soft-queue-natural-pause.md)  
