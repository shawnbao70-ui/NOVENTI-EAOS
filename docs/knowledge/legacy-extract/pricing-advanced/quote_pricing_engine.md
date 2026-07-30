# 报价计价引擎与行价计算

## Scope与证据强度

本页只深化报价行计算、汇总、改价和批准边界。通用价格公式见 [`../finance/pricing.md`](../finance/pricing.md)，折扣见 [`../commercial-terms/discount_rules.md`](../commercial-terms/discount_rules.md)；此处不复制其完整结论。

强证据覆盖 `add_quote_item`、Approve 行修订、报价汇总和复制。独立 Product Pricing Engine 是可运行试算，但没有写回报价。`pricing_rules`、AI 报价引擎和工业模型没有形成可验证的报价规则执行器。

## 业务规则（稳定ID）

1. **QPE-R01** 新增报价行必须先取得产品；取不到产品时返回报价详情且不写行。
2. **QPE-R02** 提交成本大于零则采用人工成本，否则采用产品主数据成本。
3. **QPE-R03** 新增行单价按 `cost / (1 - profit_rate/100)` 反推，`profit_rate` 在此是目标销售毛利率。
4. **QPE-R04** 单位利润为单价减成本，行金额为数量乘单价；单价、利润、金额在形成时舍入两位。
5. **QPE-R05** 报价头总额通过 `SUM(quote_items.amount)` 重算，而不是信任客户端总额。
6. **QPE-R06** 详情加载重新汇总总额、总成本、毛利，并把总额/毛利写回报价头。
7. **QPE-R07** Draft Approve 允许人工直接修改数量和单价；服务端以保存的行成本重算金额、单位利润和毛利率。
8. **QPE-R08** Approve 改价后的毛利率为 `(price-cost)/price`；单价为零时置 0，避免除零。
9. **QPE-R09** 批准必须满足 Draft、有行项和人工确认，成功后状态变为 Sent；转 SO 仍是独立动作。
10. **QPE-R10** 删除行后只重算头总额；详情/批准加载再负责头毛利刷新。
11. **QPE-R11** 复制报价按旧行值复制数量、成本、毛利率、单价和金额，不重新执行定价。
12. **QPE-R12** 客户价格历史只提供人工参考；AI/历史建议不得静默改变报价。
13. **QPE-R13** 独立 Pricing Engine 采用“成本加成→折扣→汇率折算”另一公式，结果只返回模板上下文，不写 `quote_items`。
14. **QPE-R14** 报价运行行模型没有折扣字段；折扣页面/模板槽位不能证明主链执行折扣。
15. **QPE-R15** 报价头币种和汇率不参与新增行公式；行价只隐含属于头币种。

## 流程

### 新增行

1. 客户报价已存在，用户选择产品并输入数量、成本、目标毛利率。
2. 服务读取产品，并在输入成本无效时回退主成本。
3. 服务反推单价，计算单位利润和行金额。
4. 一次写入行快照字段，再按数据库行金额重算报价总额。
5. 返回报价详情；详情计算总成本和毛利并回写报价头。

### Draft Approve 改价

1. Approve 页面读取行、总额、总成本、毛利和库存。
2. 用户可修改数量/单价；非 Draft 页面为只读。
3. 服务端逐行验证并更新，按保存成本重算盈利字段。
4. 服务重新取行并刷新报价头总额和毛利。
5. 保存草稿只停留在 Approve；批准还需状态、非空行和人工确认校验。
6. 成功批准进入 Sent。

### 独立试算边界

Finance 试算器接受总成本、加成率、折扣率和汇率，产生显示结果。它不读取报价行、不命中价目规则、不保存价格版本，也不构成报价主链。

## 校验（强/弱/缺失）

1. **QPE-V01（强）** 产品必须存在。
2. **QPE-V02（强）** Approve 修改数量必须大于零。
3. **QPE-V03（强）** Approve 修改单价不得小于零。
4. **QPE-V04（强）** 只有 Draft 可批准。
5. **QPE-V05（强）** 批准前至少有一条报价行。
6. **QPE-V06（强）** 批准必须提交 `human_confirm=1`。
7. **QPE-V07（强）** 状态更新只接受 Draft/Sent/Negotiating/Won/Lost。
8. **QPE-V08（弱）** 页面数量输入 required，Approve 页面还有 `min=0.0001`；新增行服务本身未见正数校验。
9. **QPE-V09（缺失）** 新增行未校验毛利率小于 100%，可能除零或产生负单价。
10. **QPE-V10（缺失）** 新增行未见单价、金额上限和 NaN/Infinity 业务校验。
11. **QPE-V11（缺失）** 未见最低价格、最低毛利、折扣授权或负毛利审批门。
12. **QPE-V12（缺失）** 未见并发版本校验；详情加载和批准均可回写汇总。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `qty` | 报价数量 |
| `cost_price` | 报价采用的单位成本快照 |
| `profit_rate` | 新增时为目标毛利率，改价后为结果毛利率 |
| `price` | 报价行单位成交/报出价 |
| `profit` | 单位利润，不乘数量 |
| `amount` | 数量乘单价 |
| `total_amount` | 行金额合计 |
| `total_cost` | 页面计算的数量乘行成本合计 |
| `gross_profit` | 总额减总成本，保存于报价头 |
| `margin_pct` | `gross_profit / total_amount × 100` |
| `products.sale_price` | 产品参考销售价；不进入新增行主公式 |
| `last_unit_price` | 客户+产品最近正数报价价建议 |
| `discount_rate` | 仅独立试算输入，非报价行字段 |
| `exchange_rate` | 报价头/独立试算字段；不进入报价行主公式 |

## 状态词汇

| 状态 | 计价含义 |
|---|---|
| `Draft` | 可在 Approve 改数量/单价 |
| `Sent` | 人工批准后状态 |
| `Negotiating` | 可由状态动作设置；是否仍允许专门改价入口不明确 |
| `Won` / `Lost` | 商业结果状态 |
| Save Draft | 保存行修订但不推进状态 |
| Human Approved | 明确人工确认后 Draft→Sent |
| 试算 | 只显示结果，不持久化 |

## 证据表

| # | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| QPE-E01 | 新增行公式和成本回退 | 强 | `apps/quotation/services.py` |
| QPE-E02 | 行快照字段及头 SUM | 强 | `apps/quotation/repository.py` |
| QPE-E03 | 详情加载汇总并回写毛利 | 强 | `apps/quotation/services.py` |
| QPE-E04 | Approve 服务端改量改价并重算 | 强 | `apps/quotation/services.py`、`repository.py` |
| QPE-E05 | Draft/行项/人工确认批准门 | 强 | `apps/quotation/services.py`、`templates/quote_approve.html` |
| QPE-E06 | 页面展示成本、毛利、历史价与添加行 | 强 | `templates/quote_detail.html` |
| QPE-E07 | 复制沿用旧行计算结果 | 强 | `apps/quotation/services.py`、`repository.py` |
| QPE-E08 | 独立加成/折扣/汇率公式不写报价 | 强 | `apps/finance/finance_ops_pages.py`、`templates/product_pricing_engine.html` |
| QPE-E09 | 报价行 DDL 无折扣和币种字段 | 强 | `runtime/v14/legacy_support.py` |
| QPE-E10 | V18 报告确认 Approve 可选改价和人工确认 | 中 | `docs/reports/V18_Quote_Approve_Gate_Report.md` |

## UNKNOWN + 已查路径

1. **目标毛利率的法定/业务上限 UNKNOWN。** 已查路径：`apps/quotation/`、报价模板、`docs/reports/`。
2. **新增行数量是否允许零或负数在其他中间件被拦截 UNKNOWN。** 已查路径：`apps/quotation/router.py`、`services.py`、`validator.py`、模板。
3. **报价编辑的完整价格审计（旧值、新值、原因）UNKNOWN。** 已查路径：`apps/quotation/history.py`、Approve 服务、报告。
4. **`pricing_rules` 是否有外部规则执行器 UNKNOWN。** 已查路径：`business_modules/quotation.md`、`business_modules/finance.md`、`apps/quotation/`、`apps/finance/`。
5. **税、折扣、运费的正式计算次序 UNKNOWN。** 已查路径：报价服务、打印模板、Finance、商业条款知识页。
6. **报价总额回写的并发覆盖策略 UNKNOWN。** 已查路径：`apps/quotation/repository.py`、`services.py`。
7. **Negotiating/Sent 后的正式改价版本流程 UNKNOWN。** 已查路径：报价路由、history、quote versions DDL、模板。
8. **舍入应按行、按头还是按币种最小单位 UNKNOWN。** 已查路径：报价服务、Finance 试算、模板、locale formatter。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\quote_detail.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\quote_approve.html`
- `H:\Workspace\EZAM_CRM - 9.0\templates\product_pricing_engine.html`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
