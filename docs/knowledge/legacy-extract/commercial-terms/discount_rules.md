# 折扣、优惠与特价规则

## Scope与证据强度

本页覆盖报价行定价、整单折扣、特价、价目表、审批阈值、税费次序、复制/转 SO/打印传播、权限与币种。

- **强证据：** Quotation/Sales 的运行服务、仓储、DDL、V18 Approve 路径和 NDE 构建器。
- **中证据：** 独立 Pricing Engine 可计算折扣，但不写回报价；打印模板有折扣槽，但主链未填值。
- **弱证据：** Product Pricing Rule、经销商等级、AI 风险标签和 Enterprise Rule Engine 未成为报价运行权威。
- **明确缺失：** 报价行折扣、整单折扣、special price 与运行价目表未形成贯通的数据模型。

## 业务规则

1. **DR-R01** 报价主链不是“标价减折扣”，而是由成本和毛利率反算成交单价。
2. **DR-R02** 添加报价行时，输入成本不大于零会回退产品主数据成本。
3. **DR-R03** 行金额等于数量乘成交单价；没有行折扣扣减步骤。
4. **DR-R04** 报价头总额是行金额汇总；头毛利由总额减行成本总额得到。
5. **DR-R05** V18 Approve 可在确认前修改数量和成交单价，并重算毛利、毛利率、行金额和头汇总。
6. **DR-R06** V18 Approve 仅要求 Draft、有行项和人工确认；没有折扣率或毛利阈值的强制审批门。
7. **DR-R07** 独立 Product Pricing Engine 依次计算成本加成、折扣和汇率折算，但其结果不写回 `quote_items`。
8. **DR-R08** Quotation AI 页面虽出现折扣率输入，运行路由只提供占位上下文，未证明存在计算提交链。
9. **DR-R09** Quote 复制传播商业头、成本、毛利率、成交价和金额；不传播折扣元数据，因为主数据模型没有该字段。
10. **DR-R10** Quote 转 SO 只传播产品、数量、成交价和金额；SO 不保留成本、毛利率或折扣依据。
11. **DR-R11** NDE 报价打印将行折扣留空，头折扣默认为零；模板中的折扣列不证明业务折扣存在。
12. **DR-R12** 打印规范把头折扣放在小计之后、运费/保险/其他和 VAT 之前，但报价主链未计算这些折扣值。
13. **DR-R13** AI 语义层可对低于 8% 的毛利提示风险，但该提示不阻断 Approve 或转 SO。
14. **DR-R14** `product_price_rules` 与经销商等级折扣是未接入报价主链的字段/表级预留。
15. **DR-R15** Enterprise Rule Engine 声明 discount/pricing 类型，但运行结果回退 Legacy，不接管当前定价。
16. **DR-R16** 语音建报价优先参考客户历史成交价反推毛利率，否则使用默认毛利率；它仍产生“毛利率定价”，不是折扣。
17. **DR-R17** 产品 `sale_price` 可供展示或提示，但新增报价行的主公式不以它作为折扣基准价。
18. **DR-R18** 报价币种和汇率属于头信息；行定价公式本身未进行跨币种换算。

## 流程

### 报价主链

1. 用户选择产品、数量、成本和毛利率。
2. 系统必要时回退产品成本，再按毛利率反算成交单价。
3. 系统计算行金额，并重算报价总额与毛利。
4. Approve 页面可直接改数量或成交价；系统反算并更新盈利数据。
5. 人工确认后 Draft 变为 Sent。
6. 转 SO 时仅复制成交结果，不复制折扣或成本逻辑。
7. 打印时 NDE 输出成交价与金额，折扣槽保持空或零。

### 独立定价计算器

1. 用户输入成本、加成率、折扣率和汇率。
2. 页面先计算加成售价，再减折扣，并形成汇率折算展示。
3. 结果停留在计算器上下文；未见写回报价或产品价目表。

## 校验

1. **DR-V01** Approve 修改后的数量必须大于零。
2. **DR-V02** Approve 修改后的成交价不得小于零。
3. **DR-V03** 只有 Draft 报价可进入 Approve 动作。
4. **DR-V04** Approve 前至少要有一个报价行。
5. **DR-V05** Approve 必须提交明确的人工确认值。
6. **DR-V06** 报价状态更新只接受既定状态集合。
7. **DR-V07** Quote 转 SO 前检查 Quote 存在及是否已有 SO。
8. **DR-V08** 报价新增、编辑、删除及查看成本分别受模块权限控制。
9. **DR-V09** 系统未校验折扣率是否位于 0–100，因为报价主链无折扣字段。
10. **DR-V10** 毛利率接近或达到 100% 会使反算分母为零；主链未见明确上界校验。
11. **DR-V11** 低毛利 AI 标签只是建议，不是服务端阻断。
12. **DR-V12** 转 SO 的浏览器确认只是前端交互，不能替代后端商业阈值检查。

## 数据含义

| 数据 | 含义 |
|---|---|
| `quote_items.cost_price` | 报价行成本快照 |
| `quote_items.profit_rate` | 毛利率，不是折扣率 |
| `quote_items.price` | 成交单价，可由毛利率反算或 Approve 直接改写 |
| `quote_items.profit` | 单位毛利 |
| `quote_items.amount` | 数量乘成交单价，未扣行折扣 |
| `quotes.total_amount` | 报价行金额总和 |
| `quotes.gross_profit` | 报价总毛利 |
| `quotes.currency` | 报价头币种 |
| `quotes.exchange_rate` | 报价头汇率；未进入行主公式 |
| `products.sale_price` | 产品标价/销售价，不是报价折扣基准的运行权威 |
| `product_price_rules.discount_rate` | 价格规则预留折扣率，未接报价主链 |
| `product_price_rules.final_price` | 价格规则预留最终价 |
| `distributor_levels.discount_rate` | 经销商等级折扣预留 |
| `nde.financial.discount` | 打印头折扣槽，报价路径默认为零 |
| `line.discount` | 打印行折扣槽，报价路径为空 |

## 状态词汇

| 状态 | 含义 |
|---|---|
| `Draft` | 可编辑、可发起 V18 Approve |
| `Sent` | V18 人工确认后的状态 |
| `Negotiating` | 谈判中 |
| `Won` / `Lost` | 赢单/丢单 |
| `已确认` | 转 SO 后写入的另一套确认词 |
| `Pending` | 预留审批表的默认状态，不是 V18 Approve 主链权威 |
| `Open` | SO 审批后的开放态 |
| `DEFER_TO_LEGACY` | Rule Engine 不接管 Legacy 定价 |

## 证据表

| # | 观察事实 | 证据强度 | 只读路径 |
|---|---|---|---|
| E1 | 行价按成本和毛利率反算 | 强 | `apps/quotation/services.py` |
| E2 | 报价行 DDL 无 discount 列 | 强 | `runtime/v14/legacy_support.py` |
| E3 | Approve 可改价并重算，但不查折扣阈值 | 强 | `apps/quotation/services.py`、`apps/quotation/repository.py` |
| E4 | 独立计算器含折扣但不写报价 | 强 | `apps/finance/finance_ops_pages.py`、`templates/product_pricing_engine.html` |
| E5 | NDE 行折扣为空、头折扣默认零 | 强 | `document/nde_engine.py` |
| E6 | 转 SO 只复制成交字段 | 强 | `apps/sales/services.py`、`apps/sales/repository.py` |
| E7 | 低毛利只形成语义风险提示 | 中 | `v15/ai_operating_depth/semantics.py` |
| E8 | 价格规则表存在但无主链引用 | 中 | `runtime/v14/legacy_support.py` |
| E9 | Enterprise Rule Engine 回退 Legacy | 弱 | `core/rule/`、`docs/core/Enterprise_Rule_Model.md` |
| E10 | Customs Center 未发现折扣/定价规则 | 强（缺失证据） | `apps/customs_center/` |

## UNKNOWN

1. **special price 的私有分支实现 UNKNOWN。** 已查：全库 Python、HTML、Markdown 中的 `special_price` 及同义词。
2. **运行 `pricing_rules` 表 UNKNOWN/未落地。** 已查：`business_modules/quotation.md`、Legacy DDL 与全库建表语句。
3. **产品价目表 `product_prices` 的运行链 UNKNOWN。** 已查：`business_modules/product.md`、`apps/product/`、Legacy DDL。
4. **Quotation AI 折扣 POST 是否存在于未纳入工作区的历史版本 UNKNOWN。** 已查：`apps/quotation/router.py`、Legacy 备份入口。
5. **数值型折扣审批阈值配置 UNKNOWN。** 已查：V18 Quote gate、审批模板、`docs/reports/`。
6. **预留 `quote_approval` 何时进入业务主链 UNKNOWN。** 已查：创建工具、服务和路由引用。
7. **SO/Invoice 是否应继承未来头折扣 UNKNOWN。** 已查：`apps/sales/`、Sales DDL 和打印构建器。
8. **折扣与 VAT 的正式税务计算顺序 UNKNOWN。** 已查：NDE 模板、Finance/Tax Center；只证明展示顺序。
9. **Data Hub `price_list` 导入映射 UNKNOWN。** 已查：`core/datahub/` 与功能开关。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customs_center\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\product\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ux\master_defaults.py`
- `H:\Workspace\EZAM_CRM - 9.0\v15\ai_operating_depth\semantics.py`
- `H:\Workspace\EZAM_CRM - 9.0\core\rule\`
- `H:\Workspace\EZAM_CRM - 9.0\core\datahub\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\design\DOCUMENT_COMPONENT_SPECIFICATION.md`
