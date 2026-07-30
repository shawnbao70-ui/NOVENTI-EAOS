# sample.product_id → quote_items 带入判定

**Evidence strength:** Strong negative for automatic carry-over  
**结论：** `samples.product_id` **没有**在 Sample→Quote 动作中自动写入 `quote_items.product_id`。它是样品绑定/物化结果，不是报价行物化指令；新报价只建头，产品行须由用户后续人工增加。

## 业务规则

| ID | 规则 |
|---|---|
| SPTL-R01 | Sample 可通过绑定动作取得 `product_id`，但绑定与创建 Quote 是两个独立事务。 |
| SPTL-R02 | Create Quote from Sample 只按 sample id 读取样品头。 |
| SPTL-R03 | 新 Quote 继承 sample 的 `customer_id`，并在头保存 `sample_id`。 |
| SPTL-R04 | 新 Quote 固定以 Draft 创建；INSERT 不写头总额，空报价零值依赖 schema 默认。 |
| SPTL-R05 | 该路径没有读取 `sample.product_id` 作为 line source。 |
| SPTL-R06 | 该路径没有调用 `add_quote_item` 或 quote-item insert。 |
| SPTL-R07 | 已绑定 product 的 Sample 与未绑定 product 的 Sample，在建 Quote 行方面结果相同：零行。 |
| SPTL-R08 | Sample materialize/入库流程可使用 product_id，但不会反向补 Quote 行。 |
| SPTL-R09 | 后续人工加行才读取产品成本并计算 qty/price/amount。 |
| SPTL-R10 | 人工选择的报价产品不要求等于 `sample.product_id`。 |
| SPTL-R11 | 样品数量、measurement、target_price 均不自动成为报价行字段。 |
| SPTL-R12 | lifecycle helper 只补来源追溯，不补报价行。 |
| SPTL-R13 | 同一 Sample 可重复创建多个独立空行 Draft，没有去重门。 |
| SPTL-R14 | Copy Quote 复制旧 Quote 行，不回读来源 Sample 的 product_id。 |
| SPTL-R15 | legacy residual 同名路径也只建 Quote 头，不能作为自动带行的备用实现。 |

## 字段传播矩阵

| Sample 数据 | Quote 目标 | 自动带入 | 说明 |
|---|---|---|---|
| `id` | `quotes.sample_id` | 是 | 头级来源引用 |
| `customer_id` | `quotes.customer_id` | 是/可空 | 头级客户 |
| `product_id` | `quote_items.product_id` | **否** | 未读、未 insert |
| 样品数量 | `quote_items.qty` | 否 | 无明确源字段 |
| target price | `quote_items.price` | 否 | 不参与 add line |
| measurement | 行规格/remark | 否 | 无映射 |
| material/quality | 行描述 | 否 | 无映射 |
| requirement/opportunity | Quote 头追溯 | best-effort | 与行无关 |

## 校验

| ID | 校验点 | 实际强度 |
|---|---|---|
| SPTL-V01 | path sample_id 必须是整数 | Hard type |
| SPTL-V02 | Sample 必须存在 | Missing |
| SPTL-V03 | Sample 必须绑定 product | Missing |
| SPTL-V04 | product 必须有效/可销售 | Missing at create |
| SPTL-V05 | Sample 必须达到可报价状态 | Missing |
| SPTL-V06 | product 自动成为候选行 | Missing |
| SPTL-V07 | qty 必须有明确来源且 >0 | Missing |
| SPTL-V08 | target price 必须被复核 | Missing |
| SPTL-V09 | customer 必须非空且有效 | Missing |
| SPTL-V10 | 同 Sample 只能有一个活动 Quote | Missing |
| SPTL-V11 | lifecycle link 成功才提交 | Missing；best-effort |
| SPTL-V12 | 服务端 Samples.view/Quotes.add | 未见该 handler 显式双门 |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `samples.id` | Sample 主键和转换 path id |
| `samples.product_id` | 样品绑定到产品目录的 FK |
| sample materialize | 样品侧绑定/库存语义，不等于报价行生成 |
| `quotes.sample_id` | Quote 头到来源 Sample 的直接追溯 |
| `quotes.customer_id` | 从 Sample 继承的客户，可为空 |
| `quotes.status=Draft` | 新报价初态 |
| `quotes.total_amount` | 创建 INSERT 未写；未有行时依赖 schema 默认 |
| `quote_items.product_id` | 报价行产品；此路径不写 |
| `quote_items.qty` | 报价数量；Sample 无自动映射 |
| `quote_items.cost` | 人工加行时读取/形成的成本快照 |
| `quote_items.price` | 人工加行计价结果，不取 sample target price |
| `requirement_id/opportunity_id` | 可选头追溯，不是行来源 |
| Copy Quote | 从旧 Quote 复制行，而非从 Sample 重物化 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| SPTL-E01 | Route 直接调用 create_quote_from_sample | 强 | `apps/quotation/router.py` |
| SPTL-E02 | Service 读取 Sample 后只组织 Quote 头 | 强 | `apps/quotation/services.py::create_quote_from_sample` |
| SPTL-E03 | Repository insert 只写 quotes | 强 | `apps/quotation/repository.py::insert_quote_from_sample` |
| SPTL-E04 | 创建链无 quote_items insert | 强负向 | `apps/quotation/services.py`、`repository.py` |
| SPTL-E05 | product binding 是 Sample 独立动作 | 强 | `apps/sample/services.py`、`repository.py::bind_sample_product` |
| SPTL-E06 | 人工 add line 才选择产品并计价 | 强 | `apps/quotation/services.py::add_quote_item` |
| SPTL-E07 | lifecycle helper 只写 link/头 FK | 强 | `v15/business_lifecycle/workflow.py` |
| SPTL-E08 | Sample360 CTA 未提供行选择 | 强 | `templates/sample360.html` |
| SPTL-E09 | A-005 报告验证桥接/追溯，未证明带行 | 中等佐证 | `docs/reports/Business_Strong_A005_Sample_Quote_Report.md` |

## UNKNOWN + 已查路径

1. **product_id 应自动建行还是只作为候选 UNKNOWN。** 已查：`apps/sample/**`、`apps/quotation/**`、Sample360、A-005。
2. **默认 qty 应取哪个 Sample 字段 UNKNOWN。** 已查：sample schema、measurements、requirements、quote item service。
3. **target_price 应作参考价、上限还是初始成交价 UNKNOWN。** 已查：sample requirements、quotation pricing、reports。
4. **一个 Sample 多 product/多规格的行拆分规则 UNKNOWN。** 已查：Sample service/repository、business_modules、templates。
5. **绑定产品失效时是否允许建 Quote UNKNOWN。** 已查：product binding、create quote route/service、validators。
6. **人工行产品应否被限制为 sample.product_id UNKNOWN。** 已查：add_quote_item、quote templates、router。
7. **未来补行后头总额重算的事务边界 UNKNOWN。** 已查：Quotation service/repository、pricing path。

## 交叉引用

- 权威行选择说明：[`../sample-quote-bridge-deepen/line_selection.md`](../sample-quote-bridge-deepen/line_selection.md)
- 来源追溯：[`../sample-quote-bridge-deepen/source_traceability.md`](../sample-quote-bridge-deepen/source_traceability.md)
- 报价行计价：[`../quotation-deepen/quote_lines_pricing.md`](../quotation-deepen/quote_lines_pricing.md)
