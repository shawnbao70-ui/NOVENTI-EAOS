# ADR-0321 — Phoenix Gate Framework（Decision Summary + Generated Artifacts）

**状态：** Accepted · **Formal Standard / Sole Gate Framework**  
**日期：** 2026-07-24  
**里程碑：** 未分配；本 ADR 不创建业务实现里程碑。Package 实施另见独立 Coding Authorization（standing record 2026-07-29）  
**归属：** Governance / Product Architecture（全 Business Package 共用）  
**授权：** Product Owner **Approve**（2026-07-24 pilot；2026-07-28 formal-standard；**2026-07-29 Framework Redesign review Approve** — governance process only）· **Standing Coding Authorization Approved 2026-07-29** for Gate-Accepted Business Packages — [PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md](../project/PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md)（does not waive Decision Summary for future architecture changes）  
**修改权限：** 未经 Product Owner 明确批准不得修改 Framework

## 背景

既有 Product / Architecture Gate 在原则上正确：Accepted knowledge ≠ Gate Accept ≠ 可编码；Architecture Accept 与 Coding Authorization 必须分离。但对单一 Product Owner 而言，要求阅读长篇 Gate 并手工填写 OD/RC/Approval/Evidence 表，运营成本过高，且容易把“填表”误当成治理本身。

需要在不削弱架构治理的前提下，把 Product Owner 的工作收束为**决策**，把文书工作收束为**系统生成的治理制品**。

## 决策

### 0. 唯一标准与旧流程退役

Phoenix Gate Framework 是所有 Business Package 的**唯一 Gate Framework**。
Package 不得定义独立流程、字段别名或第二套 Gate 标准。

下列人工流程立即退役，不再作为准入要求：

- Product Owner 人工填写 OD / RC
- Product Owner 人工维护 Approval Table / Signature / Evidence
- Product Owner 阅读或编辑长篇 Gate / Acceptance 作为审批前提
- 直接提交 Gate 文档绕过 Decision Summary

历史文档保留为证据，不批量改写其事实内容；其后续解释与任何增量 Gate
统一受本 ADR 约束。

### 1. 强制 Decision Summary（一屏）

每个 Business Package Product Gate 在 Product Owner 决策前，必须先提供一屏 **Decision Summary**（亦称 Authorization Summary），且只包含：

1. Package  
2. Purpose  
3. Scope  
4. Architecture Boundary  
5. In Scope  
6. Out of Scope  
7. Open Decisions  
8. Risks  
9. Recommendation  

Product Owner **不得**被要求先阅读完整 Gate / Acceptance 长文再决策。长文是生成后的治理证据，不是 PO 决策界面。

### 2. Product Owner 仅三选一

Product Owner 对 Decision Summary 只作：

- **Approve** — 接受 design boundary only  
- **Amend** — 仅允许简洁意见；Architect 修订 Summary 后重新决策  
- **Reject** — 保持 Proposed；不生成 Accept；不进入编码路径  

Product Owner **不**手工编辑 OD-01…N、RC-01…N、Approval rows、Evidence tables 或 Gate 正文。

### 3. Approve 后系统生成治理制品

在 Product Owner **Approve** 之后，由 Architect/Agent/系统生成（而非 PO 手填）：

- Architecture Gate 文档  
- Gate Acceptance 文档
- OD dispositions  
- RC attestations  
- Approval record  
- Signature section  
- Evidence section  

每份生成 Gate 必须自动包含：

1. ADR-0321 及 Package ADR 引用
2. 已批准 Decision Summary 引用
3. Evidence 引用
4. Approval Record
5. Signature
6. `Coding Authorization: None`

生成物状态固定为：

```text
Gate Accepted（design boundary only）
Coding authorization: None
Implementation milestone: None（除非另有独立 Coding Authorization）
```

### 4. Architecture Accept ≠ Coding Authorization

以下状态继续严格分离，本框架不得合并：

1. **Accepted knowledge** — 设计输入  
2. **Gate Accept（design boundary only）** — 产品/架构边界接受  
3. **Coding Authorization** — 独立的实现授权 + 已分配里程碑  

Gate Accept **永不**授权 CRUD、SQL/API/服务、Alembic、runtime `manifest.json` 注册/发布/安装，或自开实现里程碑。

三种状态之间**没有自动转换**：Accepted Knowledge 不自动接受 Gate；
Gate Accepted 不自动授予 Coding Authorization；Coding Authorization 也不
回写或重定义前两种状态。

### 5. 全 Package 统一流程

下列及未来 Business Package **必须**使用同一 Phoenix Gate Framework，不得另起一套 Gate 工作流：

CRM · Inventory · Purchase · Finance · Approval · Workflow · Marketplace · Enterprise Brain · 其他业务包

仅 Decision Summary 内容变化；程序不分支。

统一状态流固定为：

```text
Decision Summary
→ PO Decision
→ Generator
→ Gate Accepted
→ independent Coding Authorization
→ Implementation
```

### 6. 与 Dual-Track / Architecture Review 的关系

- Dual-Track：基线绿（Track A）与草案证据（Track B）可喂给 Decision Summary；Product Owner 决策即 Track G。  
- Architecture Review：Summary **不能**豁免 RC / Kernel 污染 / fail-closed 不变量；ARB 仍可对生成物 Hold。  
- CRM Customer + Contact Authorization Summary 视为本框架的 **pilot**，应逐步对齐本 ADR 字段名与生成规则。

## 后果

- Product Owner 决策面降为一屏 + 三选项。  
- 治理深度保留在生成制品与 Architecture Review 中。  
- 代理提示词从“请 PO 填 OD/RC”改为“请 PO Approve/Amend/Reject Summary”。  
- 后续业务包不得再要求 PO 手工维护 Acceptance 表单作为准入条件。

## 非目标

- 不授权任何业务 Package 实现或 CRUD  
- 不合并 Architecture Accept 与 Coding Authorization  
- 不削弱 Tenant / Permission / Audit / Event / Package≠Kernel 不变量  
- 不要求本 ADR 同步 DAL Usage、运行包版本或 Alembic head  
- 不打开 Brain execute / Twin authorize
- 不修改 Repository/CRUD/Database/API/Runtime/Frontend/Business Logic
- 本次正式化不授予 Coding Authorization

## 历史兼容

CRM、Inventory、Purchase、Finance、Workflow、Marketplace、Enterprise Brain
及已有 Approval 文档均迁移到本 Framework 的解释边界。迁移不表示重新批准、
不改变历史证据、不自动授予 Coding Authorization，也不建立第二套标准。

## Approval Record

- Decision Summary：[Phoenix Gate Framework Decision Summary](../project/PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md)
- Product Owner response：**Approve**（2026-07-28）
- Approval meaning：Framework design/governance boundary only
- Coding Authorization：**None**

## Signature

System-generated signature projection from the explicit Product Owner
`Approve` response. No Product Owner manual signature entry is required.

## Evidence

- [Phoenix Gate Framework](../project/PHOENIX_GATE_FRAMEWORK.md)
- [Approved Decision Summary](../project/PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md)
- [Generated Approval Record](../project/PHOENIX_GATE_FRAMEWORK_APPROVAL_RECORD.md)
- [Decision Summary template](../project/templates/BUSINESS_PACKAGE_DECISION_SUMMARY.md)
- [Generator rules](../project/PHOENIX_GATE_GENERATOR_RULES.md)
- [Legacy migration register](../project/PHOENIX_GATE_LEGACY_MIGRATION.md)

## 关联

- [Phoenix Gate Framework（操作标准）](../project/PHOENIX_GATE_FRAMEWORK.md)  
- [Decision Summary 模板](../project/templates/BUSINESS_PACKAGE_DECISION_SUMMARY.md)  
- [Coding Authorization Summary 模板](../project/templates/CODING_AUTHORIZATION_SUMMARY.md)  
- [CRM C1 Coding Authorization Summary（待 PO）](../project/CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)  
- [ADR-0029 — Business Package Platform 边界](ADR-0029-business-package-platform.md)  
- [ADR-0320 — CRM Customer + Contact Product Boundary](ADR-0320-crm-customer-contact-product-boundary.md)  
- [CRM Customer + Contact Authorization Summary（pilot）](../project/CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)  
