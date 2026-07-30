# ADR-0172 — Foundation Ops / Compatibility / Checklist Hygiene

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G153  
**归属：** Phoenix Governance / Foundation release hygiene  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U025**

## 背景

PHX-G144 将包基线升至 `0.2.1` 后，G145–G152 已 Fully Accepted（WebAuthn thin + ceremony stub、Role→grant thin、OIDC/OpenAPI product surfaces、AED、AR Board Queue、Manifest milestones）。`OPERATIONS_RUNBOOK.md` / `COMPATIBILITY.md` / `RELEASE_CHECKLIST.md` 仍主要锚定 G144/R17，未记载 stub 503、Held mint、或 Manifest G145–G152 卫生检查，运维与发布门禁易与 tip 漂移。

## 决策

1. 更新 `OPERATIONS_RUNBOOK.md`：milestones 含 G144–G153；Smoke / Out-of-scope 明确 WebAuthn ceremony stub 503、live mint Held、Role→grant mint Held、支付/Brain/Twin fail-closed；指向 AR Board Queue 为 Research 非运维开口。  
2. 更新 `COMPATIBILITY.md`：baseline 仍 `0.2.1` / Alembic `0029`；记载 G145–G152 为 additive-only 补丁面（无 schema bump）。  
3. 更新 `RELEASE_CHECKLIST.md`：Foundation `0.2.1` 持续检查项含 Manifest milestones G145–G152、七步自审含近期 Acceptance。  
4. PHX-G153 为 **docs-only** Fully Accepted；无 Gateway/Kernel 代码、无新 Alembic、无包 bump。  
5. **不**打开 live WebAuthn mint、Role→grant mint、Eng `4`、Brain execute、Twin authorize、AR Board self-certify。

## Explicit Out（本切片不开口）

- Live WebAuthn create/get / attestation mint  
- Role→grant auto-write / mint（explicit PO）  
- Marketplace 支付清算 / 外部仲裁（Eng `4` 暂缓）  
- Brain execute / Twin authorize  
- 全量 OpenAPI HTTP parity  
- Const/BP rewrite / AR Board decision fill  
- 新 Alembic / 包版本 bump  

## 后果

- 运维与发布检查与 G145–G152 tip 对齐；下一「继续」仍按 AED deepen order。

## 关联

- [../release/OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)  
- [../release/COMPATIBILITY.md](../release/COMPATIBILITY.md)  
- [../release/RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)  
- [../project/PHX-G153_ARCHITECTURE_GATE.md](../project/PHX-G153_ARCHITECTURE_GATE.md)  
- [../project/PHX-G153_ACCEPTANCE.md](../project/PHX-G153_ACCEPTANCE.md)  
- [ADR-0163-foundation-0-2-1-release-train.md](ADR-0163-foundation-0-2-1-release-train.md)  
- [ADR-0171-architecture-review-board-queue-and-release-hygiene.md](ADR-0171-architecture-review-board-queue-and-release-hygiene.md)  
