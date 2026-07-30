# ADR-0176 — Foundation Ops / Checklist Hygiene After G156

**状态：** Accepted  
**日期：** 2026-07-21  
**里程碑：** PHX-G157  
**归属：** Phoenix Governance / Foundation release hygiene  
**授权：** DAL-G003 + DAL-G004（AED v1.1）；Usage **DAL-U029**

## 背景

PHX-G154（WebAuthn stub observability）、PHX-G155（T2/T3 readiness）、PHX-G156（Role→grant auto-write stub）已 Fully Accepted，但 `OPERATIONS_RUNBOOK.md` / `RELEASE_CHECKLIST.md` 仍主要锚定 G153，Smoke 未记载 G154 `ceremony_step` 与 G156 `POST /permission/role-grants` → 503，运维门禁易与 tip 漂移。全量 OpenAPI HTTP（T-0188 remainder）仍过大，不宜作为本切片。

## 决策

1. 更新 `OPERATIONS_RUNBOOK.md`：milestones 含 G144–G157；Smoke 含 G154 observability 与 G156 Role→grant stub 503；Held fences 区分 stub vs live mint（PO）。  
2. 更新 `RELEASE_CHECKLIST.md`：Manifest milestones G145…G157；Acceptance 指针含 G156/G157；Role→grant stub vs mint Held。  
3. `COMPATIBILITY.md` 追加 PHX-G157 行（若尚未对齐）。  
4. PHX-G157 为 **docs-only** Fully Accepted；无 Gateway/Kernel 代码、无新 Alembic、包版本保持 **`0.2.1`**、Alembic head 保持 **`0029`**。  
5. **不**打开 live mint（WebAuthn / Role→grant）、Eng `4`、Brain execute、Twin authorize、全量 OpenAPI HTTP。

## Explicit Out（本切片不开口）

- Live WebAuthn create/get mint  
- Role→grant live mint（**explicit PO**）  
- Marketplace 支付清算（Eng `4`）  
- Brain execute / Twin authorize  
- 全量 OpenAPI HTTP parity（T-0188 remainder）  
- 新 Alembic / 包版本 bump / Gateway 代码  

## 后果

- 运维 Smoke 与 G154–G156 tip 对齐；下一「继续」仍按 AED（Board / live T2/T3 / mint-with-PO / 或审慎 OpenAPI）。

## 关联

- [../release/OPERATIONS_RUNBOOK.md](../release/OPERATIONS_RUNBOOK.md)  
- [../release/RELEASE_CHECKLIST.md](../release/RELEASE_CHECKLIST.md)  
- [../project/PHX-G157_ARCHITECTURE_GATE.md](../project/PHX-G157_ARCHITECTURE_GATE.md)  
- [../project/PHX-G157_ACCEPTANCE.md](../project/PHX-G157_ACCEPTANCE.md)  
- [ADR-0172-foundation-ops-compatibility-checklist-hygiene.md](ADR-0172-foundation-ops-compatibility-checklist-hygiene.md)  
- [ADR-0175-role-grant-auto-write-stub-deepen.md](ADR-0175-role-grant-auto-write-stub-deepen.md)  
