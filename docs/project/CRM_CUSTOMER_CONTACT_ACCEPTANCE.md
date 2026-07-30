# CRM Customer + Contact Product Gate Acceptance

**日期：** 2026-07-24  
**状态：** Gate Accepted（design boundary only；system-generated）  
**规范源：** [ADR-0320](../decisions/ADR-0320-crm-customer-contact-product-boundary.md)  
**Gate：** [CRM Customer + Contact Product Architecture Gate](CRM_CUSTOMER_CONTACT_ARCHITECTURE_GATE.md)  
**实现授权：** None  
**授权源：** [Approved Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)

## 使用方式

本文是 Product Owner 批准 Authorization Summary 后由系统生成的治理 artifact，不是 Product Owner 手工表单。OD dispositions、RC attestations、Approval record 与 signature 均由获批 Summary 自动填充。

## Product Owner authorization

**Decision：Approve — Accept Design Boundary（2026-07-24，explicit conversation authorization）。**  
该授权只接受 [Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md) 中的设计边界与显式 Defer；不授权编码、实现里程碑、runtime manifest 或任何业务写路径。

## Open-decision docket

下列 disposition 由系统根据 Product Owner 批准的 Authorization Summary 生成。

| ID | Approved baseline | Generated disposition |
|---|---|---|
| OD-01 | 单一 lifecycle；archive 优先于 hard delete | Accept proposed；具体词汇/restore guard 独立设计 |
| OD-02 | opaque ID 与 tenant-scoped code/name | Amend；分群/等级/来源/geography/重复识别 Defer |
| OD-03 | Customer-owned Contact child + optional primary contact | Accept proposed；细化词汇与历史策略独立设计 |
| OD-04 | 渠道唯一性/联系人去重 | Defer out of gate |
| OD-05 | 外联、外跳、同意/合法依据 | Defer out of gate；未获独立接受前保持关闭 |
| OD-06 | owner/territory | Amend；owner 仅责任引用，territory Defer，不短路 Permission |
| OD-07 | resource-scoped default-deny authorization | Amend；接受边界，详细 action/scope/masking 独立设计 |
| OD-08 | Contact PII deny/mask/audit | Amend；接受治理要求，具体策略独立设计 |
| OD-09 | 数据主体权利、驻留/跨境、法务例外 | Accept proposed；不在本 Gate 发明法域规则 |
| OD-10 | runtime event | Defer out of gate；manifest events 保持空 |
| OD-11 | 高影响/Workflow 分类 | Defer out of gate；留给独立写能力 Gate |

## Generated rejection-condition attestations

| ID | Condition absent? | Generated evidence |
|---|---|---|
| RC-01 Accepted knowledge 被当作产品接受 | False | Knowledge/design distinction explicit |
| RC-02 Tenant/Permission fail-closed 缺失 | False | Gate invariants explicit |
| RC-03 owner/role/resolve/UI 被当作授权 | False | Permission remains sole decision source |
| RC-04 Legacy owner filter 短路对象所有权 | False | Explicitly forbidden |
| RC-05 Contact privacy/retention 无责任路径 | False | Governance path retained; details deferred |
| RC-06 Legacy ID/覆盖/GET 变异/Admin 绕过/硬级联被继承 | False | Explicitly forbidden |
| RC-07 Gate 携带实现、Alembic、runtime manifest 或安装 | False | Design artifacts only |
| RC-08 台账/version/migration 更新被用来暗示 Accept | False | No promotion performed |
| RC-09 Gate Accept 被写成运行或编码授权 | False | Coding authorization remains None |

## Scope acceptance

- **Accepted:** Customer 是租户内商业客户/账户，不是 Tenant、Identity Subject、Enterprise、Org Unit、Membership 或财务科目。
- **Accepted:** Contact 是 Customer-owned child entity，不自动成为 Identity Subject、Membership 或 Permission Principal。
- **Accepted:** Customer/Contact 使用 opaque business identity，不使用 Legacy ID、名称、邮箱、电话或 Subject ID 充当身份。
- **Accepted:** owner 仅为责任引用；territory Defer；二者不产生可见性、Role、Membership 或 Grant。
- **Accepted:** Customer 使用单一 lifecycle，archive 优先于 hard delete；具体词汇/restore guard 独立设计。
- **Deferred:** 分群、等级、来源、geography、重复识别、Contact 用途词汇、reachability 历史细节。
- **Out:** Opportunity、Quote/Convert、Sales Order、Finance、Follow-up、Customer360/Object360/Graph、搜索/导入/去重、联系人角色/决策权、下游 Contact 快照、Brain/Twin。



## Ownership acceptance

- **Accepted:** `noventi.crm` 是 Business Package owner；Customer/Contact 不归 Kernel。
- **Accepted:** 数据归租户侧企业；平台与 Package 不取得经营或数据所有权。
- **Accepted:** CRM 不复制 Identity、Organization、Permission、Workflow、Event 或审计真相源。
- **Verified:** namespace 使用 `noventi.crm`、`pkg.crm.*`、`crm.*`，不占用 Kernel 保留空间。
- **Verified:** `manifest.proposed.json` 不携带安全上下文，不是 runtime contract；ResolveAction 无业务副作用。
- **Deferred:** 重命名、注册、发布、安装、read API 与 runtime manifest；schema 合法不构成授权。



## Tenant and privacy acceptance

- **Accepted:** Tenant 只来自 trusted ExecutionContext；跨租户访问/关联默认拒绝并 fail closed。
- **Accepted:** Contact PII 必须受最小化、字段可见性、masking、audit、retention、consent 与合规治理。
- **Accepted:** 数据主体权利、驻留/跨境与法务例外保留明确控制责任路径。
- **Deferred:** 渠道唯一性/去重、外联/外跳、具体 masking/audit/retention 与法域规则；未独立接受前保持关闭。



## Constitution acceptance

- **Verified:** BOOK02 企业数据主权与 Organization 边界保持。
- **Verified:** BOOK06 数据主体权利、法务例外、驻留/跨境控制路径保持。
- **Verified:** BOOK11 / Package Blueprint 的 Package/Kernal 与 Legacy non-inheritance 边界保持。
- **Verified:** BOOK19 Tenant isolation、default-deny、audit 与 fail-closed 不变量保持。
- **Verified:** BOOK23 声明式 surface/action 不覆盖安全上下文、业务真相或执行授权。



## Permission acceptance

- **Accepted:** Permission Kernel Evaluate 是唯一授权入口；resource-scoped、default-deny、fail-closed。
- **Accepted:** owner、role、Package resolve、Workflow approval 与 UI visibility 都不替代 Permission allow。
- **Accepted:** Contact PII 不因 `high_impact: false` 被视为低敏感。
- **Deferred:** 详细 action/scope/ScopeResolver/masking 矩阵与未来高影响/Workflow 分类；未独立接受前无写能力。



## Audit and event acceptance

- **Accepted:** 未来审计不可关闭，且须最小化 Contact 敏感 payload。
- **Accepted:** Gate Accept 不授权 HTTP Event.Publish 或任何 runtime event。
- **Deferred:** PII read audit 粒度、留存、event producer/schema/payload/消费者；manifest `declared_events` 保持空。



## Legacy and implementation honesty

- **Verified:** Legacy 仅为只读知识；未复制源码、SQL、表、路由、角色绕过或硬级联。
- **Verified:** Accepted knowledge、Gate Accept 与 coding authorization 继续严格分离。
- **Verified:** 未以 DAL/status/changelog/release/version/migration 更新暗示接受。
- **Required:** 独立编码授权与实现里程碑之前，不得实现 CRUD、SQL/API/服务/Repository/Alembic/UI/runtime manifest 或业务写路径。



## Gate-level negative scenarios

这些是设计评审场景，不是 API、数据库或测试实现要求。


| Scenario | Required gate outcome | Generated status |
|---|---|---|
| 无可信 Tenant context | fail closed；不得从请求字段补齐 | Satisfied by boundary |
| Contact 与 Customer Tenant 不一致 | 关联、读取与未来变更均拒绝 | Satisfied by boundary |
| 仅 owner/territory 匹配但 Permission deny | 保持 deny；责任字段不得短路求值 | Satisfied by boundary |
| Surface/action 可见但 Package 未安装或 Permission deny | 不得推导访问或执行权 | Satisfied by boundary |
| Contact detail read 涉及受限 PII | deny/mask/audit；`high_impact: false` 不改变敏感性 | Accepted principle；detail contract deferred |
| Legacy ID、邮箱或电话被用作产品身份 | 拒绝；使用 opaque identity | Satisfied by boundary |
| Customer archive 且存在 Contact/跨域引用 | 不得硬级联 | Accepted principle；detail contract deferred |
| 事件 schema/producer 未接受 | 不发布；manifest events 为空 | Satisfied by Defer |
| 只有 Accepted knowledge | 不构成设计或编码授权 | Satisfied by separation |
| Gate Accept 但无编码授权/里程碑 | 仍不可编码或注册 runtime manifest | Active restriction |
| 仅有台账/status/changelog/release/version 更新 | 不构成 Gate Accept | Satisfied；no promotion used |




## Required evidence for Gate review


| Evidence | Generated owner | Status |
|---|---|---|
| Approved Authorization Summary | Product Owner | Approved |
| Product lifecycle and scope disposition | System from approved Summary | Generated |
| Package/Kernel boundary review | System governance check | Verified |
| Constitution review (BOOK02/06/11/19/23 + Package Blueprint) | System governance check | Verified |
| Tenant/Permission boundary | System governance check | Accepted principle；detail contract deferred |
| Contact privacy/data-retention boundary | System from approved Summary | Accepted principle；detail contract deferred |
| Audit/event boundary | System from approved Summary | Runtime event deferred |
| Knowledge traceability | System governance check | Verified |
| Proposed manifest schema/link/non-runtime evidence | System schema/link checks | Verified |
| Explicit design-only Gate decision | Product Owner | Recorded |




## Approval record

| Role | Actor | Decision | Evidence/date |
|---|---|---|---|
| Product Owner | Authenticated conversation actor | Approve — Accept Design Boundary | Authorization Summary；2026-07-24 |
| System governance generator | Cursor agent | Generated OD/RC/evidence/acceptance artifacts | This document；2026-07-24 |
| Product Owner | Shawn | Phase G **Reaffirm** — design boundary only | [Retired historical Review Pack](CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md)；2026-07-26 |
| Coding authority（design Gate surface） | — | **None**（Gate Accept ≠ coding） | Remains separated |
| Coding authority（C1 independent） | Shawn | Phase G **Affirm** PHX-G294 | [Coding Authorization Summary](CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)；2026-07-26 |

## Generated human signature record

```text
CRM Customer + Contact Product Gate decision:
Decision: Accept design boundary only
Authorization source: CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md
OD-01..OD-11 dispositions: generated above
RC-01..RC-09: all False
Product Owner: authenticated conversation actor — Approve / 2026-07-24
System generator: Cursor agent — governance artifacts generated / 2026-07-24
Evidence exceptions: detailed control contracts explicitly deferred; no silent implementation decisions
Coding authorization: None
Implementation milestone: None
```

该记录由系统生成；Product Owner 无需手工编辑。它只证明 design-only Gate Accept。

## Generated consistency review

| Review | Generated finding |
|---|---|
| Architecture | Business Package ownership accepted；Kernel unchanged |
| Product scope | Customer + Contact boundary accepted；adjacent capabilities explicitly Out/Deferred |
| Knowledge honesty | Legacy single-contact evidence remains distinct from accepted Product design |
| Authorization | resource-scoped default-deny accepted；detailed matrix deferred |
| Tenant/privacy | fail-closed and PII governance accepted；control details deferred |
| Event/audit | audit principle accepted；runtime event and detailed contracts deferred |
| Implementation honesty | no CRUD/SQL/API/service/UI/Alembic/runtime manifest/milestone；coding authorization None |
## Decision record


| Decision | Current value |
|---|---|
| Accepted knowledge | Yes — ADR-0309 input is available |
| Knowledge extract gate | PHX-G290 Accepted（knowledge only） |
| Product Gate | **Gate Accepted（design boundary only）— Reaffirmed 2026-07-26** |
| Authorization workflow | Single Product Owner Approve；system-generated artifacts；Phase G human reaffirm |
| Coding authorization（design Gate） | **None**（Gate Accept ≠ 可编码） |
| Coding authorization（C1 independent） | **Affirmed — PHX-G294**（Phase G 2026-07-26） |
| Implementation milestone（C1） | **PHX-G294**（independent coding surface only） |

## Acceptance outcome

**GATE ACCEPTED — DESIGN ONLY（REAFFIRMED 2026-07-26）。**  
设计边界由 Product Owner Shawn Reaffirm。C1 编码仅由独立 Coding Authorization + Phase G Affirm（PHX-G294）覆盖；不得把 Gate Accept 解释为任意新切片或 runtime manifest 授权。

## Generated artifact index

- [Approved Authorization Summary](CRM_CUSTOMER_CONTACT_AUTHORIZATION_SUMMARY.md)
- [Retired Phase G Review Pack (historical evidence only)](CRM_CUSTOMER_CONTACT_GATE_ACCEPT_REVIEW_PACK.md)
- [Coding Authorization Summary (C1 / PHX-G294)](CRM_CUSTOMER_CONTACT_CODING_AUTHORIZATION_SUMMARY.md)
- [Proposed manifest](../../packages/crm/manifest.proposed.json)
- [Customer Legacy Knowledge](../knowledge/legacy-extract/crm/customer.md)
- [Contacts & Roles Legacy Knowledge](../knowledge/legacy-extract/customer-deepen/contacts_roles.md)

