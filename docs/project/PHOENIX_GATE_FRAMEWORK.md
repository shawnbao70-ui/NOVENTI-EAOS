# Phoenix Gate Framework

**状态：** **Formal Accepted Standard · Sole Gate Framework**（ADR-0321）  
**日期：** 2026-07-24；Product Owner reaffirmed 2026-07-28  
**适用范围：** 所有 Business Package Product / Architecture Gates  
**Coding authorization：** 本文件永不授予
**修改权限：** Product Owner explicit approval only

## 一句话

Product Owner 做决策；系统生成 Gate 文书；编码授权永远另走。

## 标准流程

```text
Decision Summary (one page; only approval entry)
        │
        ▼
Product Owner: Approve | Amend | Reject
        │
        ├─ Amend  → revise Summary → re-decide
        ├─ Reject → remain Proposed; STOP
        └─ Approve
                │
                ▼
        Generator creates all governance artifacts
        Gate Accepted (design boundary only)
        Coding authorization = None
                │
                ▼
        Independent Coding Authorization
        + assigned milestone
                │
                ▼
        Implementation slice allowed
```

## Decision Summary（强制，一屏）

字段顺序固定：

| # | Field |
|---|---|
| 1 | Package |
| 2 | Purpose |
| 3 | Scope |
| 4 | Architecture Boundary |
| 5 | In Scope |
| 6 | Out of Scope |
| 7 | Open Decisions |
| 8 | Risks |
| 9 | Recommendation |

模板：[templates/BUSINESS_PACKAGE_DECISION_SUMMARY.md](templates/BUSINESS_PACKAGE_DECISION_SUMMARY.md)

## Product Owner 界面

只允许：

- **Approve**
- **Amend: \<concise comment\>**
- **Reject**

禁止要求 Product Owner：

- 阅读完整 Gate/Acceptance 长文后才决策  
- 手工填写 OD/RC/Evidence/Approval 表  
- 兼任五角色逐行签名作为默认路径（单 PO 场景下由 Approve 投影生成签署记录）
- 编辑 Gate、OD、RC、Checklist、Evidence、Approval Record 或 Signature
- 绕过 Summary 直接审批 Gate 文档

旧式人工 OD/RC/Approval/Signature/Evidence 流程已退役。历史文档仅作证据保留。

## Approve 后必须生成的制品

1. Architecture Gate 文档  
2. Gate Acceptance 文档
3. OD dispositions  
4. RC attestations  
5. Approval record  
6. Signature section  
7. Evidence section  

生成规则：[PHOENIX_GATE_GENERATOR_RULES.md](PHOENIX_GATE_GENERATOR_RULES.md)  
标准 Gate 模板：[templates/GENERATED_ARCHITECTURE_GATE.md](templates/GENERATED_ARCHITECTURE_GATE.md)
标准 Acceptance 模板：[templates/GENERATED_ACCEPTANCE.md](templates/GENERATED_ACCEPTANCE.md)

每份生成物必须显式包含：

```text
ADR reference: <link>
Decision Summary reference: <link>
Evidence reference: <link>
Approval Record: generated from explicit PO decision
Signature: generated projection
Gate Accepted（design boundary only）
Coding authorization: None
```

除非另有独立 Coding Authorization 记录，否则不得暗示可编码。

## Coding Authorization（独立第二决策）

Architecture Gate Accept 之后，若要实施，必须另有 **Coding Authorization**
（不得由 Gate Accept 自动推导）。

模板：[templates/CODING_AUTHORIZATION_SUMMARY.md](templates/CODING_AUTHORIZATION_SUMMARY.md)

Product Owner 同样只回：`Approve` / `Amend` / `Reject`。  
Slice-level Summary 应列出由排队真源推导的下一合法里程碑；Product Owner
只作 `Approve` / `Amend` / `Reject`，不手工填写里程碑或 Checklist。

### Standing Coding Authorization（2026-07-29）

Product Owner issued standing **Coding Authorization Approved** for all
Business Packages that already hold Architecture Gate Accepted. Record:
[PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md](PHOENIX_GATE_STANDING_CODING_AUTHORIZATION.md).

That standing auth permits implementation activities inside accepted
boundaries; it does **not** waive Decision Summary for future architecture
changes, hard holds, or one-contiguous-milestone sequencing. Next slice still
follows the queue truth source after **FINAL STOP TRACK-G518** (or successor).

CRM C1 历史示例：[CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md](CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)

## 不可变治理原则

1. Accepted Knowledge ≠ Architecture Gate Accepted ≠ Coding Authorization  
   三种状态独立；任何状态变化均不得自动触发另外两个状态。
2. Package ≠ Kernel；不得把业务真相塞进 Kernel  
3. Tenant / Permission default-deny / Audit / Event Outbox 不变量不可被 Summary 豁免  
4. Architecture Review 仍可对 RC 违规或 Kernel 污染 Hold  
5. Dual-Track：A 基线证据与 B 草案证据可输入 Summary；不得跳过 Summary 直接手改 Accepted

## 适用 Package（非穷尽）

CRM · Inventory · Purchase · Finance · Approval · Workflow · Marketplace · Enterprise Brain · 未来业务包

任一 Package 需要不同 Gate 工作流 → **拒绝**；应修订本框架，而不是开旁路。

## 历史兼容

CRM · Inventory · Purchase · Finance · Workflow · Marketplace · Enterprise Brain
统一迁移到本 Framework 的解释边界，见
[PHOENIX_GATE_LEGACY_MIGRATION.md](PHOENIX_GATE_LEGACY_MIGRATION.md)。
迁移保留原始证据和批准日期，不重新批准、不自动授权编码。

## 实施边界

本 Framework 正式化仅修改 Governance Framework、ADR、Gate Documents、
Decision Summary 与 Generator Rules。它不授权或修改 CRUD、Database、API、
Runtime、Frontend、Business Logic 或 Runtime Manifest。

## Approval Record / Signature / Evidence

- Product Owner：explicit **Approve**（2026-07-28）
- Approved Summary：[PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md](PHOENIX_GATE_FRAMEWORK_DECISION_SUMMARY.md)
- Generated record：[PHOENIX_GATE_FRAMEWORK_APPROVAL_RECORD.md](PHOENIX_GATE_FRAMEWORK_APPROVAL_RECORD.md)
- Generated Gate：[PHOENIX_GATE_FRAMEWORK_ARCHITECTURE_GATE.md](PHOENIX_GATE_FRAMEWORK_ARCHITECTURE_GATE.md)
- Generated Acceptance：[PHOENIX_GATE_FRAMEWORK_ACCEPTANCE.md](PHOENIX_GATE_FRAMEWORK_ACCEPTANCE.md)
- Scope：Framework governance boundary only
- Coding Authorization：**None**
- Signature：system-generated projection；无需 PO 手填
- Evidence：[ADR-0321](../decisions/ADR-0321-phoenix-gate-framework.md) ·
  [Decision Summary template](templates/BUSINESS_PACKAGE_DECISION_SUMMARY.md) ·
  [Generator rules](PHOENIX_GATE_GENERATOR_RULES.md)

## Pilot

[CRM Customer + Contact Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md) 是本框架试点。后续 Package 必须直接使用标准 Decision Summary 模板与本流程。

## 关联

- [ADR-0321 — Phoenix Gate Framework](../decisions/ADR-0321-phoenix-gate-framework.md)  
- [ADR-0320 — CRM Customer + Contact Product Boundary](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)  
