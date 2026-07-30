# Sample / Requirement / Opportunity → Quote 追溯

**Evidence strength:** Strong for fields/helpers; medium for end-to-end completeness because failures degrade silently  
**Cross-references:** [`../opportunity-requirement-deepen/README.md`](../opportunity-requirement-deepen/README.md)、[`../sample-deepen/README.md`](../sample-deepen/README.md)、[`../quotation-deepen/README.md`](../quotation-deepen/README.md)

## Scope 与关键结论

Legacy 使用三层追溯：Quote 上的直接字段、Requirement 头的单值下游指针，以及 `requirement_links` 多值关系。Sample→Quote 主创建直接保存 `quotes.sample_id`；requirement/opportunity 由 lifecycle helper 条件传播。helper 会检查列、捕获查询/关系异常并分步 commit，因此报价可成功而追溯部分缺失。

## 业务规则

| ID | 规则 |
|---|---|
| STR-R01 | Sample→Quote INSERT 直接保存 `quotes.sample_id`。 |
| STR-R02 | 新报价 customer_id 从 sample.customer_id 继承，与追溯字段分离。 |
| STR-R03 | 创建后调用 `link_quote_from_sample`，调用本身被 try/except 包裹。 |
| STR-R04 | helper 重新读取 sample；读取失败或样品不存在时静默返回。 |
| STR-R05 | quotes 有对应列时才写 sample_id/requirement_id/opportunity_id。 |
| STR-R06 | sample.requirement_id 存在时，覆盖 `business_requirements.quote_id`。 |
| STR-R07 | requirement_links 表存在时追加 quote/from_sample 关系。 |
| STR-R08 | sample.opportunity_id 存在时传播到 quote；不存在时不从 requirement 再推断。 |
| STR-R09 | 需求直转报价使用 `link_quote_from_requirement`，传播 requirement_id 及需求的 opportunity_id。 |
| STR-R10 | direct 路径覆盖 requirement.quote_id，并追加 quote/direct link。 |
| STR-R11 | Quote→SO 主路径复制 requirement_id/opportunity_id 到 sales order。 |
| STR-R12 | Quote→SO 再覆盖 requirement.sales_order_id 并追加 sales_order/from_quote link。 |
| STR-R13 | `_safe_update` 只写实际存在且值非 None 的列。 |
| STR-R14 | `_safe_update` 可独立 commit，多表传播不是单一原子事务。 |
| STR-R15 | requirement_links 追加异常被吞掉，主体 Quote/SO 不回滚。 |
| STR-R16 | Requirement 头 quote_id 是单值快捷指针，多次生成时被最新写覆盖。 |
| STR-R17 | requirement_links 可并存多条关系，但未见唯一防重。 |
| STR-R18 | context360 依据字段即时查询上下游，查询失败返回空列表，页面可隐藏追溯缺口。 |
| STR-R19 | Sample context 按 `sample_id OR requirement_id` 找 Quote，可能把同需求其他报价也展示为下游。 |
| STR-R20 | 普通报价只有显式 requirement_id 时建立 direct link，不自动推断来源。 |
| STR-R21 | Copy Quote 不调用 lifecycle link，也不复制 sample_id/requirement_id/opportunity_id，复制后的 Draft 可与来源链断开。 |

## 追溯路径

### Sample → Quote

`samples.id → quotes.sample_id`（直接保存）  
`samples.requirement_id → quotes.requirement_id → requirement.quote_id`（条件传播）  
`samples.opportunity_id → quotes.opportunity_id`（条件传播）  
`requirement_links(role=from_sample)`（可选追加）

### Requirement → Quote

`QuoteFormData.requirement_id → quotes.requirement_id`  
`business_requirements.opportunity_id → quotes.opportunity_id`  
`business_requirements.quote_id → latest quote`  
`requirement_links(role=direct)`（可选追加）

### Quote → Sales Order

`quotes.requirement_id/opportunity_id → sales_orders.*`  
`business_requirements.sales_order_id → latest SO`  
`requirement_links(role=from_quote)`（可选追加）

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| STR-V01 | 写前检查目标列存在 | Weak/conditional |
| STR-V02 | Sample→Quote 主体保存 sample_id | Hard when column exists in INSERT schema |
| STR-V03 | sample/requirement/opportunity 记录必须存在 | Weak；查不到静默返回 |
| STR-V04 | 来源与报价 customer 一致 | Missing |
| STR-V05 | helper 必须报告写入结果 | Missing |
| STR-V06 | 直接字段、头指针、link 必须一致 | Missing |
| STR-V07 | requirement_links 必须唯一 | Missing |
| STR-V08 | 多表传播必须单事务 | Missing |
| STR-V09 | 主体成功前追溯必须完整 | Missing |
| STR-V10 | 删除/取消下游后清理指针/link | Missing |
| STR-V11 | 多报价必须选择 primary/current | Missing |
| STR-V12 | context360 查询失败必须显式告警 | Missing；返回空 |
| STR-V13 | opportunity 必须从 requirement/sample 权威来源一致传播 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.sample_id` | 报价来源样品直接字段 |
| `quotes.requirement_id` | 报价来源需求反向字段 |
| `quotes.opportunity_id` | 报价来源商机反向字段 |
| `samples.requirement_id` | 样品绑定需求 |
| `samples.opportunity_id` | 样品绑定商机，可传播 |
| `business_requirements.quote_id` | 最新写入的单值报价快捷指针 |
| `business_requirements.sales_order_id` | 最新写入的单值订单快捷指针 |
| `requirement_links.requirement_id` | 多值关系的需求端 |
| `entity_type='quote'` | link 下游对象类型 |
| `entity_id` | Quote/SO 下游 id |
| `link_role='from_sample'` | 经样品生成报价 |
| `link_role='direct'` | 需求直接生成报价 |
| `link_role='from_quote'` | 报价生成订单 |
| `updated_at` | 需求头指针覆盖时间 |
| context360 upstream/downstream | 当前字段查询投影，不是不可变审计 |
| silent degrade | 缺列/缺表/异常不阻断主体动作 |
| copied quote | 行和商业头可复制，但来源追溯字段不继承 |

## 静默降级点

| 点 | 结果 |
|---|---|
| `_fetchone` SQL 异常 | 返回空对象 |
| 目标列不存在 | `_safe_update` 跳过 |
| link 表不存在 | 不追加关系 |
| add_link 异常 | 吞掉 |
| Quotation helper 调用异常 | Quote 仍创建 |
| Sales helper 调用异常 | SO 仍创建 |
| context 查询异常 | 页面显示空关系 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| STR-E01 | Sample→Quote 直接保存 sample_id | 强 | `apps/quotation/services.py`、`repository.py` |
| STR-E02 | Sample/Requirement/Opportunity 条件传播 | 强 | `v15/business_lifecycle/workflow.py` |
| STR-E03 | requirement 头指针和 links 写入 | 强 | workflow、`repository.py` |
| STR-E04 | Quote→SO 追溯复制为 best-effort | 强 | `apps/sales/services.py`、workflow |
| STR-E05 | context360 双向投影与安全空列表 | 强 | `v15/business_lifecycle/context360.py` |
| STR-E06 | 需求创建模型含单值下游指针 | 强 | `v15/business_lifecycle/repository.py` |
| STR-E07 | 生命周期 schema/列演进 | 强 | `database/business_lifecycle_schema.py` |
| STR-E08 | A-005 gate 验证 direct requirement link | 强佐证 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| STR-E09 | Requirement 深化确认覆盖/并存模型 | 强交叉 | `../opportunity-requirement-deepen/requirement_trace.md` |
| STR-E10 | Sample 深化确认 from_sample 主链 | 强交叉 | `../sample-deepen/sample_to_quote.md` |
| STR-E11 | Copy Quote 不复制或重建 trace FK | 强负向 | `apps/quotation/services.py::copy_quote` |

## UNKNOWN + 已查路径

1. **生产各部署是否都具备 sample/requirement/opportunity 扩展列 UNKNOWN。** 已查：schema migration、workflow PRAGMA、runtime DDL、reports。
2. **一个需求多个 Quote 中哪个是 primary/current UNKNOWN。** 已查：头 quote_id、requirement_links、Requirement360。
3. **重复 requirement_links 是否已存在及如何去重 UNKNOWN。** 已查：schema、repository、三个 helper。
4. **追溯部分提交后的补偿/重试机制 UNKNOWN。** 已查：workflow、Quotation/Sales services、jobs/reports。
5. **Sample、Requirement、Opportunity 与 Quote 客户不一致是否允许 UNKNOWN。** 已查：link helper、create services、context360。
6. **下游删除/取消后头指针与 links 如何清理 UNKNOWN。** 已查：Sample/Quotation/Sales 删除、workflow、schema。
7. **context360 空关系如何区分“无关系”和“查询失败” UNKNOWN。** 已查：`_safe_fetch`、enrich、templates。
8. **追溯字段与 requirement_links 谁是审计权威 UNKNOWN。** 已查：workflow、repository、context360、reports。

## 交叉引用

- 商机/需求：[`../opportunity-requirement-deepen/README.md`](../opportunity-requirement-deepen/README.md)
- 样品：[`../sample-deepen/README.md`](../sample-deepen/README.md)
- 报价：[`../quotation-deepen/README.md`](../quotation-deepen/README.md)
