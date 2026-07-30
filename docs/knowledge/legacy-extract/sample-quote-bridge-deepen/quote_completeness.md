# 转 Sales Order 前的报价完整性

**Evidence strength:** Strong for actual Convert gates; strong negative for missing completeness enforcement

## Scope 与关键结论

Legacy 将 Quote Approve 与 Convert SO 分开。Approve 强制 Draft、有行和 Human Confirm，但 Convert SO 不要求先 Approve，也不校验行、价格、客户、salesperson、币种、有效期、样品/需求/商机追溯。Convert 的硬门只有报价存在和 `sales_orders.quote_id` 尚未出现。因此“可转换”不等于“报价完整”。

## 业务规则

| ID | 规则 |
|---|---|
| QCP-R01 | Convert 先按 id 读取报价；不存在即返回报价列表。 |
| QCP-R02 | 已存在同 quote_id SO 时不重复创建。 |
| QCP-R03 | Convert 不校验报价状态；Draft/Sent/Won/Lost 均可进入。 |
| QCP-R04 | Convert 不依赖 Quote Approve 或中心审批记录。 |
| QCP-R05 | Convert 不要求至少一条 quote item；可产生空 SO 头。 |
| QCP-R06 | Convert 不要求 customer_id 非空或客户有效。 |
| QCP-R07 | Convert 不要求 salesperson_id；直接复制现值。 |
| QCP-R08 | Convert 不校验 qty>0、price≥0 或 amount 与 qty×price 一致。 |
| QCP-R09 | Convert 复制 quote header total_amount，不在转换时按行重算。 |
| QCP-R10 | Convert 不复制币种、汇率、付款条件、有效期或 remark 到 SO。 |
| QCP-R11 | Convert 不要求报价未过期。 |
| QCP-R12 | sample_id、requirement_id、opportunity_id 不是转换硬门。 |
| QCP-R13 | Sales 主路径 best-effort 传播 requirement/opportunity 到 SO，失败不回滚。 |
| QCP-R14 | Quote Approve 有行/人工门，但只得到 Sent；转 SO仍是另一动作。 |
| QCP-R15 | SO Approve 后续要求 SO 有行，因此空 SO 可能在第二阶段才被阻断。 |
| QCP-R16 | UI Convert CTA 有权限可见性和浏览器 confirm，但 handler 本身无显式 request gate。 |
| QCP-R17 | 转单成功写报价 `已确认`，不会补齐缺失客户、行、追溯或商业条件。 |

## 完整性矩阵

| 维度 | Quote Create | Quote Approve | Convert SO |
|---|---|---|---|
| 报价存在 | 创建主体 | Hard | Hard |
| customer | 可为空路径存在 | 展示/不硬拒绝 | 不校验 |
| salesperson | 可为 0 | 不硬拒绝 | 不校验 |
| 至少一行 | 不要求 | Hard | 不要求 |
| qty>0 | 新增服务弱 | Approve patch Hard | 不重验 |
| price≥0 | 形成公式/patch Hard | Hard | 不重验 |
| total=行合计 | 多路径重算 | 重算 | 直接复制头 |
| Draft 状态 | 默认 | Hard | 不要求 |
| Human Confirm | 路径依赖 | Hard | 浏览器提示 |
| currency/FX | 有默认/可空演进 | 展示 | 不复制/不重验 |
| validity | 默认值 | 不校验到期 | 不校验 |
| sample link | 可选 | 非门 | 非门 |
| requirement/opportunity | best-effort | 非门 | best-effort 传播 |

## 强、弱、缺失分类

- **强：** quote 存在；同 quote 不得已有 SO；Approve 的 Draft/行/Human Confirm。
- **弱：** UI `Sales Orders.add` 和 confirm；头总额由其他页面重算；追溯 helper 条件写入。
- **缺失：** Convert 的状态、行、客户、owner、价格、币种、有效期、追溯完整性和并发唯一约束。

## 校验

| ID | 校验 | 强度 |
|---|---|---|
| QCP-V01 | 报价存在 | Hard |
| QCP-V02 | 同 quote 未有 SO | Hard query guard |
| QCP-V03 | 报价至少有一行 | Missing at Convert |
| QCP-V04 | customer_id 非空且客户有效 | Missing |
| QCP-V05 | salesperson_id 非空且有效 | Missing |
| QCP-V06 | qty/price/amount 合法 | Missing at Convert |
| QCP-V07 | total_amount 等于行合计 | Missing at Convert |
| QCP-V08 | 状态 Sent/Won/Approved | Missing |
| QCP-V09 | 报价未过有效期 | Missing |
| QCP-V10 | 币种/汇率/付款条件完整 | Missing |
| QCP-V11 | sample/requirement/opportunity 引用有效 | Missing |
| QCP-V12 | trace propagation 成功 | Missing；异常吞掉 |
| QCP-V13 | DB unique quote_id | UNKNOWN |
| QCP-V14 | 服务端 RBAC + POST/CSRF | Missing/weak |

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `quotes.id` | Convert 的源对象键 |
| `sales_orders.quote_id` | 重复检查和来源引用 |
| `quotes.customer_id` | 复制到 SO 的客户，可为空风险 |
| `quotes.salesperson_id` | 复制到 SO 的 owner，可为 0 |
| `quotes.total_amount` | 直接复制的头金额 |
| `quote_items` | 逐行复制来源；可为空 |
| `qty/price/amount` | SO 行复制字段，不在 Convert 重算 |
| `status` | Convert 不读取为 gate；成功后写 `已确认` |
| `currency/exchange_rate` | 报价商业头；不复制到当前 SO insert |
| `validity_days` | 报价有效期；Convert 不使用 |
| `sample_id` | 可选来源样品；不构成完整性门 |
| `requirement_id` | 可传播到 SO 的需求追溯 |
| `opportunity_id` | 可传播到 SO 的商机追溯 |
| lifecycle link | best-effort 追溯，不是事务硬门 |
| 空 SO | 有头、无行；后续 SO Approve 才拒绝 |

## 证据表

| # | 观察事实 | 强度 | 只读来源 |
|---|---|---|---|
| QCP-E01 | Convert 只有存在/重复两硬门 | 强 | `apps/sales/services.py::convert_so` |
| QCP-E02 | header 直接复制客户/owner/date/total | 强 | `apps/sales/services.py`、`repository.py` |
| QCP-E03 | 行复制循环允许空集合 | 强 | `apps/sales/services.py::_copy_quote_items_to_so` |
| QCP-E04 | Convert 不检查状态/有效期/商业头 | 强负向 | `apps/sales/services.py` |
| QCP-E05 | Quote Approve 三门与 Convert 分离 | 强 | `apps/quotation/services.py` |
| QCP-E06 | Sample→Quote 可创建空行 Draft | 强 | `apps/quotation/services.py::create_quote_from_sample` |
| QCP-E07 | lifecycle link best-effort 且吞异常 | 强 | `apps/sales/services.py`、`v15/business_lifecycle/workflow.py` |
| QCP-E08 | SO Approve 空行门 | 强 | `apps/sales/services.py::apply_so_approve` |
| QCP-E09 | UI权限/confirm 与 GET handler差异 | 强 | `templates/quotes.html`、`apps/sales/router.py` |
| QCP-E10 | 既有 Convert 深化结论 | 强交叉 | `../quotation-deepen/quote_convert_gates.md` |

## UNKNOWN + 已查路径

1. **业务政策是否允许 Draft/Lost 报价直接转 SO UNKNOWN。** 已查：Quotation/Sales services、business modules、reports。
2. **空报价转空 SO 是有意场景还是缺陷 UNKNOWN。** 已查：Convert、SO Approve、templates、A/V18 reports。
3. **客户为空或已失效时下游约束 UNKNOWN。** 已查：Quotation/Sales repositories、customer 状态、convert。
4. **报价有效期是否应硬阻断转换 UNKNOWN。** 已查：validity 字段、Quote services/templates、Sales convert。
5. **币种/汇率为何不复制到 SO及后续金额币种 UNKNOWN。** 已查：Quote/SO schema、conversion、finance。
6. **追溯 helper 部分失败后的补偿/重试 UNKNOWN。** 已查：workflow、Sales service、jobs/reports。
7. **数据库是否唯一约束 sales_orders.quote_id UNKNOWN。** 已查：Sales repository、runtime DDL、升级脚本。
8. **多行转换中途失败的事务回滚范围 UNKNOWN。** 已查：Sales service/repository commit 点。

## 交叉引用

- 转单门槛：[`../quotation-deepen/quote_convert_gates.md`](../quotation-deepen/quote_convert_gates.md)
- 报价批准：[`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md)
- 行选择：[`line_selection.md`](line_selection.md)
