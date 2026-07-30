# ADR-0162 — Dual-Track Governance

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G143  
**归属：** Phoenix Governance / NRI Alignment  
**人工批准：** Product Owner accepted Architecture Decision Report (Dual-Track); Chief Architect delegated to execute documentation and sequencing

## 背景

Phoenix Foundation 已达 `0.2.0` / PHX-G142；工程软队列实质耗尽。NOVENTI 已识别多项未来能力（Enterprise Discovery、DNA、Capability First、Organization Neutrality、AI Workforce、Evolution Engine、Future EOM 等），仍属研究概念。NRI Charter v1.0 已存在，但 Phoenix 长期模式是否为「单一工程路线图」未在战略层正式裁决。

## 决策

1. **Adopt Dual-Track Governance** 作为 Project Phoenix 长期治理方向。  
2. **Engineering Track**：Foundation 稳定、编号硬延后、发布列车、ADR/Gate/Acceptance、实现。  
3. **Research Track (NRI)**：永久研究产品；`docs/research/**`；不得直接改 Constitution / Blueprint / Kernel / Runtime / 生产实现。  
4. **唯一合法桥梁**：NRI Promotion Rules — Research Library → Architecture Review → Blueprint → Constitution Review → ADR/Gate → Implementation → Release（晋升可选；留在 Library 为合法终态）。  
5. **Constitution 最高**；生产 fail-closed（Brain execute、Twin authorize、支付清算等）不受研究紧迫性打开。  
6. 工程软队列为空时，默认推进 Research Track 或 Eng 发布质量；**禁止**发明未晋升的产品开口。  
7. 本 ADR **不**修改 Constitution BOOK、Blueprint、Kernel、Runtime、数据库。

## Explicit Defer（仍属 Engineering Track，需编号/另批）

- ~~Foundation `0.2.1` 发布列车~~ → **PHX-G144 / ADR-0163 Accepted**  
- Full WebAuthn / MFA registration product page  
- Role→grant 自动写入  
- Marketplace 支付清算 / 外部仲裁  
- 多区域生产 SaaS / failover（非目标）

## 后果

- `docs/project/DUAL_TRACK_GOVERNANCE.md` 为操作手册（策略、迁移、同步、执行序）。  
- MASTER_PLAN / ROADMAP / PROJECT_STATUS / NRI 交叉引用对齐 Dual-Track。  
- 「继续」在 Eng 侧仅推进编号硬延后或已批准 Eng 切片；战略能力默认 NRI。

## 关联

- [DUAL_TRACK_GOVERNANCE.md](../project/DUAL_TRACK_GOVERNANCE.md)  
- [PHX-G143_ARCHITECTURE_GATE.md](../project/PHX-G143_ARCHITECTURE_GATE.md)  
- [../research/RESEARCH_GOVERNANCE_CHARTER.md](../research/RESEARCH_GOVERNANCE_CHARTER.md)  
- [../research/RESEARCH_PROMOTION_RULES.md](../research/RESEARCH_PROMOTION_RULES.md)  
