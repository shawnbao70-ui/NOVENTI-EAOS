# Legacy Knowledge Extract — Customer Deepen Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/customer-deepen/**`  
**Verified:** 2026-07-23

## Scope

本包深化 Legacy 客户主数据中的集团/门店层级、联系人角色、客户状态与信用冻结，以及 Customer360 应收余额视图。它只陈述可观察规则、缺失校验和数据语义，不把 Object360/Business Graph 架构词汇、UI 风险带或 `organizations.parent_id` 推断为已实施客户能力。

## Modules

- [Customer Hierarchy](customer_hierarchy.md) — 扁平客户主档与集团/总部/门店缺口
- [Contacts & Roles](contacts_roles.md) — 单一联系人字段与决策角色缺口
- [Customer Status Lifecycle](customer_status_lifecycle.md) — 可编辑状态标签、冻结/黑名单缺口
- [Customer AR Balance View](ar_balance_view.md) — Customer360 的 SO−Receipt 经营余额、Statement 的 AR 台账口径及财务交界
- 汇总见 [INDEX.md](INDEX.md)

## Evidence posture

- `customers` 是扁平主表，报价、订单、交付和收款按单一 `customer_id` 关联；未发现客户父级/集团/门店模型。
- 联系人是客户行上的姓名、电话、WhatsApp 和邮箱字段；未发现多联系人、角色、主联系人、决策权或同意模型。
- `customer_status` 可直接编辑并用于不一致的 Dashboard 分组；未发现状态机、冻结、客户黑名单或信用 hold。
- `credit_limit` 等扩展槽位存在，但未接入报价、订单或交付 gate；余额风险带只是启发式展示。
- Customer360 应收余额是客户 SO 总额减 Receipt 总额；Customer Statement 则读取 `ar_records.balance`，两者没有多币种转换、勾兑或差异披露。
- Object360 运行时主要复用 Legacy 上下文；架构 bridges 和 Graph 类型不改变客户主档权威。

## Hard boundaries

- 客户等级 A/B/C/D 不是集团层级，也不是经审批的信用等级。
- `organizations.parent_id` 是平台组织结构，不是客户母子关系。
- Customer Graph `contact`/`has_contact` 不证明联系人主数据已实现。
- `暂停跟进`、`失效客户` 不等于执行冻结；`ip_blacklist` 不是客户黑名单。
- Customer360 的 Credit Watch 和 A/B/C/D 风险带不是授信决策。
- SO−Receipt 客户余额不是 `ar_records` 子账余额，也不证明逐笔核销。
