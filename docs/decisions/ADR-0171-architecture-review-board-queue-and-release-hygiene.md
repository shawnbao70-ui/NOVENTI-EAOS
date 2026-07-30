# ADR-0171 — Architecture Review Board Queue + Foundation Release Hygiene

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G152  
**归属：** Phoenix Governance / Dual-Track（Research tip + Foundation hygiene）  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U024**

## 背景

RP-001…010 Architecture Review Candidate Packages（NRI-ARC-RP-001…010）已全部打开且 Awaiting Board，但分散在 G2 tip 与各 program 目录，Board 缺少单一 standing queue。同时 `RELEASE_MANIFEST.yaml` 里程碑仅记到 PHX-G144，未反映 G145–G151 已 Fully Accepted 的 Foundation 切片，release hygiene 落后于 PROJECT_STATUS。

## 决策

1. 新增 docs-only standing queue：`docs/research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md`（**NRI-AR-BOARD-QUEUE**），汇总 10 个 Candidate Package、Wave 顺序 hint、关键 invariants；**不**填写 Board decision、**不**自证 Promote/Hold/Reject。  
2. Foundation release hygiene：在 `RELEASE_MANIFEST.yaml` `milestones` 追加 PHX-G145…G151（及本切片 G152）为 `fully_accepted`；包版本仍 **`0.2.1`**；Alembic 仍 **`0029`**。  
3. PHX-G152 为 **docs-only** Fully Accepted；无 Gateway/Kernel 代码、无新 Alembic、无包 bump。  
4. **不**打开 Eng `4` 支付清算、Brain execute、Twin authorize、live WebAuthn mint、Role→grant mint（mint 仍需 explicit PO）。

## Explicit Out（本切片不开口）

- Architecture Review Board self-certify / 代填 decision block  
- Eng soft-queue invent from Research queue alone  
- Live WebAuthn create/get mint  
- Role→grant auto-write / mint（explicit PO）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- Const/BP content rewrite as production truth  
- 新 Alembic / 包版本 bump  

## 后果

- Board 可从单一队列调度 NRI-ARC-RP-001…010。  
- Manifest 里程碑与 G145–G152 status 对齐；下一「继续」仍按 AED deepen order。

## 关联

- [../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md](../research/ARCHITECTURE_REVIEW_BOARD_QUEUE.md)  
- [../project/PHX-G152_ARCHITECTURE_GATE.md](../project/PHX-G152_ARCHITECTURE_GATE.md)  
- [../project/PHX-G152_ACCEPTANCE.md](../project/PHX-G152_ACCEPTANCE.md)  
- [../release/RELEASE_MANIFEST.yaml](../release/RELEASE_MANIFEST.yaml)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
- [ADR-0162-dual-track-governance.md](ADR-0162-dual-track-governance.md)  
- [ADR-0169-autonomous-execution-directive.md](ADR-0169-autonomous-execution-directive.md)  
