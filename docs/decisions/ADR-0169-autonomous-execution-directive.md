# ADR-0169 — Autonomous Execution Directive (AED)

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G150  
**归属：** Phoenix Governance / Dual-Track Operating Directive  
**授权：** DAL-G003 + **DAL-G004**（DAL-U012）

## 背景

Dual-Track（ADR-0162）与持续自主窗口（DAL-G003 through 2026-07-27）已生效，但「继续」仍多为聊天口令，易与 Explicit Defer / HARD HOLDS / Research invent 边界冲突。Product Owner 提出 *Autonomous Execution Directive* v1.0；经架构审核修订为 v1.1 后，需落为规范性工件，而非静默覆盖 playbook。

## 决策

1. 采纳修订后的 **Autonomous Execution Directive v1.1** 为 Dual-Track **operating directive**（[AUTONOMOUS_EXECUTION_DIRECTIVE.md](../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)）。  
2. AED **supersedes** 仅依赖聊天「继续」的任务选择方式；**不**修改 Constitution / Blueprint / Kernel / Runtime。  
3. 记录 **HARD HOLDS**（不可自主开口）：Eng Explicit Defer `4` 支付清算暂缓；Brain execute；Twin authorize；Cap≠grant；不 invent 未知 peers；不自证 Architecture Review Board 裁决；不以 Const/BP rewrite 为生产真相。  
4. **Explicit Defer 规则：** 在 DAL 窗口内（through 2026-07-27），Eng `1`–`3` deepenings 可在 charter-safe + Architecture Gate + DAL Usage Log 下推进；Eng `4` **始终**需 PO；窗口外一切 Explicit Defer 需 PO。  
5. **价值平局：** Architectural quality + risk avoidance **优先于** business narrative。  
6. **Research 默认产出（G1 完成后）：** Architecture Review Candidate Packages + T2/T3 evidence — **不** invent 新 RP IDs / 不 speculative WP invent。  
7. **加深优先序：** Foundation harden / contracts / release hygiene → WebAuthn ceremony → AR Candidates → Role→grant mint（mint 即使在自主窗口内仍需 **explicit PO**）→ full OpenAPI HTTP。  
8. 每个里程碑强制 **milestone report** + **DAL Usage Log**。  
9. PHX-G150 为 **docs-only** Fully Accepted；包仍 `0.2.1`；Alembic 仍 `0029`。

## Explicit Out（本切片不开口）

- Eng `4` 支付清算  
- Brain execute / Twin authorize  
- Role→grant mint / WebAuthn ceremony 产品实现  
- Constitution / Blueprint / Kernel / Runtime 内容改写  
- Architecture Review Board 自证 Promote/Hold/Reject  
- 新 Alembic / 包版本 bump  

## 后果

- 「继续」= 在 HARD HOLDS 下按 AED 选择最高价值任务；非按序号 invent 产品开口。  
- DAL-G004 Active 叠加 G003；Usage **DAL-U012**（本 ADR/AED/G150）与后续 Research deepen（如 DAL-U013）须记账。  
- Dual-Track playbook、Eng tip、Research tip 指向 AED v1.1。

## 关联

- [../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md](../project/AUTONOMOUS_EXECUTION_DIRECTIVE.md)  
- [../project/PHX-G150_ARCHITECTURE_GATE.md](../project/PHX-G150_ARCHITECTURE_GATE.md)  
- [../project/PHX-G150_ACCEPTANCE.md](../project/PHX-G150_ACCEPTANCE.md)  
- [../project/DELEGATED_AUTHORITY_LEDGER.md](../project/DELEGATED_AUTHORITY_LEDGER.md)  
- [../project/DUAL_TRACK_GOVERNANCE.md](../project/DUAL_TRACK_GOVERNANCE.md)  
- [ADR-0162-dual-track-governance.md](ADR-0162-dual-track-governance.md)  
