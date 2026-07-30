# Sample → Quote 行选择、带入与空行草稿

**Evidence strength:** Strong for header-only creation and absence of automatic lines

## Scope 与关键结论

`/create_quote_from_sample/{sample_id}` 的活动服务只读取样品客户、创建 Draft 报价头、保存 sample_id 和商业头默认，然后尝试补充追溯。它没有查询 sample product/measurement/requirement/matching 来选择报价行，也没有调用 quote item insert。即使 sample 不存在，服务仍可能以空客户创建 sample_id 指向无效值的 Draft。报价行必须后续人工添加。

## 业务规则

| ID | 规则 |
|---|---|
| LSL-R01 | Sample360 的 Create Quote 是人工 GET 动作，页面使用浏览器 confirm。 |
| LSL-R02 | 服务按 `QT` + 秒级时间戳生成新报价号。 |
| LSL-R03 | 样品存在且有 customer_id 时，新报价继承该客户。 |
| LSL-R04 | 样品不存在或无客户时，customer_id 可为空，主体创建不被硬阻断。 |
| LSL-R05 | 新报价日期为服务器当天、状态为 Draft、总额为初始零。 |
| LSL-R06 | 报价头直接保存来源 sample_id。 |
| LSL-R07 | 币种、汇率、有效期、付款和交期来自客户/品牌/平台默认链。 |
| LSL-R08 | 创建路径不读取 `samples.product_id` 来自动生成报价行。 |
| LSL-R09 | 样品测量、材料、图片、质量和 supplier matching 不形成报价行。 |
| LSL-R10 | `sample_requirements.target_price` 不自动成为报价行价格。 |
| LSL-R11 | 服务不调用 `add_quote_item` 或 quote item repository insert。 |
| LSL-R12 | 新 Draft 可以 `quote_items` 为空，用户之后在报价详情人工选产品。 |
| LSL-R13 | 人工新增行再按产品成本和目标毛利率计价，与 Sample 转换动作分离。 |
| LSL-R14 | sample product 无效、未绑定或未 materialize 均不阻止创建报价头。 |
| LSL-R15 | 同一样品没有查重 gate，可重复建立多个空行 Draft。 |
| LSL-R16 | 样品状态不会被更新为 Converted/Quoted。 |
| LSL-R17 | 转样报价不设置 salesperson_id，按业务员过滤时可见性可能受影响。 |
| LSL-R18 | legacy 同名实现也只创建头；其商业头能力更弱，但同样不自动建行。 |

## 行选择/带入/跳过矩阵

| Sample 数据 | 是否带入 Quote | 结果 |
|---|---|---|
| customer_id | 是，带入头 | 可为空 |
| sample id | 是，带入头 | `quotes.sample_id` |
| product_id | 否 | 不建 quote item |
| sample quantity | 否 | 不作为报价 qty |
| measurements | 否 | 不建行规格 |
| material analysis | 否 | 不建行描述 |
| target_price | 否 | 不写 price |
| supplier matching | 否 | 不选产品/供应商 |
| images | 否 | 不附报价行 |
| requirement/opportunity | best-effort 追溯 | 不影响行 |
| commercial defaults | 是，带入头 | 不影响行选择 |

## 空行草稿证据链

1. `insert_quote_from_sample` 只插 quotes 头字段。
2. 服务随后只更新 commercial header 和调用 lifecycle helper。
3. 该路径没有 item insert。
4. Draft 可直接打开详情，行集合为空、头总额为零。
5. Quote Approve 会以“至少一行”阻断，但 Convert SO 不要求行，因此空头 SO 仍可能被创建。

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| LSL-V01 | 路由 sample_id 为整数 | Hard type |
| LSL-V02 | 页面浏览器确认 | UI only |
| LSL-V03 | 样品必须存在 | Missing |
| LSL-V04 | 样品客户必须存在/有效 | Missing |
| LSL-V05 | 样品必须绑定 product | Missing |
| LSL-V06 | 样品状态/分析必须可报价 | Missing |
| LSL-V07 | 至少选择一条报价行 | Missing at create；Approve hard |
| LSL-V08 | 行数量必须来自明确来源 | Missing |
| LSL-V09 | target price/产品价格必须复核 | Missing |
| LSL-V10 | 同 sample 只允许一个活动报价 | Missing |
| LSL-V11 | Quotes.add / Samples.view 服务端权限 | Missing |
| LSL-V12 | salesperson 必须确定 | Missing |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| path `sample_id` | 转换动作的来源 id |
| `samples.customer_id` | 报价客户来源 |
| `samples.product_id` | 样品目录绑定；此路径不用于建行 |
| `quotes.sample_id` | Quote→Sample 直接追溯 |
| `quotes.customer_id` | 从样品继承，可为空 |
| `quote_no` | 时间戳生成的新业务号 |
| `quote_date` | 创建当天 |
| `Draft` | 转样报价初始状态 |
| `total_amount` | 新头初始零，等待行汇总 |
| `quote_items` | 创建时为空的行集合 |
| commercial header | 客户历史/品牌/平台默认快照 |
| `sample_requirements.target_price` | 参考字段，不自动传播 |
| `salesperson_id` | 此路径未设置的报价 owner |
| `Converted/Quoted` | 样品未写入的状态语义 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| LSL-E01 | 路由直接调用 Sample→Quote service | 强 | `apps/quotation/router.py` |
| LSL-E02 | 服务读取样品并创建 Draft 头 | 强 | `apps/quotation/services.py::create_quote_from_sample` |
| LSL-E03 | repository 只 INSERT quotes 头 | 强 | `apps/quotation/repository.py::insert_quote_from_sample` |
| LSL-E04 | 路径无 quote item insert | 强负向 | `apps/quotation/services.py`、`repository.py` |
| LSL-E05 | Sample360 CTA 与确认 | 强 | `templates/sample360.html` |
| LSL-E06 | Lifecycle helper 只写追溯字段 | 强 | `v15/business_lifecycle/workflow.py` |
| LSL-E07 | A-005 报告覆盖 Sample/Quote/Requirement | 强佐证 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |
| LSL-E08 | 普通新增行公式与产品选择独立 | 强 | `apps/quotation/services.py::add_quote_item` |
| LSL-E09 | legacy 同名头创建实现 | 强 | `apps/quotation/quote_pages.py` |

## UNKNOWN + 已查路径

1. **样品 product_id 应否默认成为候选报价行 UNKNOWN。** 已查：Sample repository/services、Quotation create/add item、templates、A-005。
2. **样品数量应从哪个字段带入报价 qty UNKNOWN。** 已查：samples DDL、sample measurements/requirements、Quotation line path。
3. **target_price 应作为参考、上限还是成交价 UNKNOWN。** 已查：sample_requirements、pricing、Quote templates/reports。
4. **不存在样品仍创建 Draft 是否被全局中间件阻止 UNKNOWN。** 已查：router、service、repository、middleware。
5. **同一样品多个报价的主/有效报价选择规则 UNKNOWN。** 已查：sample_id 查询、context360、Quotation service。
6. **样品分析完成的可报价条件 UNKNOWN。** 已查：Sample status、analysis/quality tables、Sample360 CTA。
7. **转样报价 salesperson 应取当前用户、客户 owner 还是需求 owner UNKNOWN。** 已查：普通报价、样品报价、customer/salesperson、列表过滤。

## 交叉引用

- 样品桥接基线：[`../sample-deepen/sample_to_quote.md`](../sample-deepen/sample_to_quote.md)
- 报价计价：[`../quotation-deepen/quote_lines_pricing.md`](../quotation-deepen/quote_lines_pricing.md)
- 空行转 SO 风险：[`quote_completeness.md`](quote_completeness.md)
