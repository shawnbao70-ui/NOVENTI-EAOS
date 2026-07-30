# 商务条款转单传播（Commercial Term Propagation）— Legacy Knowledge

**Evidence strength:** Strong for quote header persistence and SO insert field set; strong negative for full-term propagation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块核对报价币种/汇率/有效期/付款条款/交期/备注、客户信用、折扣、税、Incoterms 在 Quote→SO 时是否传播。结论是：Convert 只复制客户、业务员、报价日期、总额和成交行；完整商业头没有进入 SO schema/insert，后续 Receipt/AR 又使用独立默认。

交叉引用 `../commercial-terms/**` 和 `../pricing-advanced/**`，不复制其大段内容。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CTP-R1 | Quote 持久化 currency 与 exchange_rate | 属报价商业头 |
| CTP-R2 | Quote 持久化 validity_days | 表示报价有效期，不是账期 |
| CTP-R3 | Quote 持久化 payment_term | 可打印的自由文本 |
| CTP-R4 | Quote 持久化 delivery_time | 交期文本，不是 Incoterm |
| CTP-R5 | Quote 持久化 remark | 商业备注 |
| CTP-R6 | 新建/复制/样品报价可通过 defaults 传播这些头字段 | 报价内部传播较完整 |
| CTP-R7 | Convert SO header 只复制 quote/customer/salesperson/date/total 与状态 | 不含商业头字段 |
| CTP-R8 | SO schema/insert 未保存 quote currency/exchange_rate | SO 金额币种变为隐含 |
| CTP-R9 | payment_term 不传播到 SO | SO 只有 payment progress |
| CTP-R10 | validity_days 不传播，也不作为 Convert gate | 过期报价仍可转 |
| CTP-R11 | delivery_time/remark 不传播到 SO | 履约团队无法依赖 SO header |
| CTP-R12 | Quote 行只复制 product/qty/price/amount | cost、profit、discount 依据不复制 |
| CTP-R13 | 报价主链无行/头 discount 字段 | 传播的是净成交价，不是折扣政策 |
| CTP-R14 | NDE discount 槽为空或零 | 文档槽不证明运行折扣 |
| CTP-R15 | customer credit_limit/payment_days 不进入 Convert gate | 不冻结信用快照 |
| CTP-R16 | customer status/blacklist/freeze 不阻断 Convert | Legacy 无完整客户交易冻结 |
| CTP-R17 | Quote/SO 主链没有 Incoterms/named place 字段 | 不存在可传播来源 |
| CTP-R18 | Customs registry metadata 不写 Quote/SO | 不能补足传播 |
| CTP-R19 | Quote tax/VAT 展示槽未形成可证 header-to-SO contract | SO insert 无税字段 |
| CTP-R20 | SO total 与 line price/amount 原样复制 | 不按 FX、折扣或税重新计算 |
| CTP-R21 | Receipt 快捷路径固定 USD | 不从 Quote/SO 继承币种 |
| CTP-R22 | DO→AR 仅写金额且无币种/条款 | 账期与 FX 链断裂 |
| CTP-R23 | NDE Quote 可显示商业头，但 SO/Statement 使用各自上下文 | 文档展示不等于数据传播 |
| CTP-R24 | EAOS 不得把 SO 金额默认为 USD 或本位币 | Legacy 缺少显式币种事实 |

---

## 3. Process

### 3.1 Quote 商业头形成

1. 默认链从客户最近报价、品牌和平台默认解析。
2. Quote 保存 currency、rate、validity、payment、delivery、remark。
3. 报价行按成本/毛利或直接改价形成 price/amount。
4. Approve 展示并发布报价，但不重新解释商业头。

### 3.2 Convert 传播

1. 读取 quote header。
2. SO 仅接收 customer、salesperson、quote date、total。
3. 行仅接收 product、qty、price、amount。
4. currency、rate、validity、payment term、delivery time、remark、credit、discount、tax、Incoterms 均无对应写入。

### 3.3 下游

1. SO payment status 从未收开始。
2. Receipt 以 USD/Bank Transfer 默认建立。
3. DO 复制 SO 金额，Post AR 写无币种 `ar_records`。
4. 未观察到付款天数推导 due date、FX 损益或贸易责任传播。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CTP-V1 | quote 必须存在且未有 SO | Hard | |
| CTP-V2 | commercial header 必须完整才可 Convert | Missing | |
| CTP-V3 | quote 必须未过 validity | Missing | |
| CTP-V4 | currency 必须活动且 rate > 0 | Missing | |
| CTP-V5 | SO 必须保存 document currency/FX snapshot | Missing | |
| CTP-V6 | payment term 必须传播并计算 due date | Missing | |
| CTP-V7 | credit limit/payment days 必须校验 | Missing | |
| CTP-V8 | discount/margin threshold 必须审批 | Missing | |
| CTP-V9 | Incoterm + named place 必须成对 | Missing | |
| CTP-V10 | tax mode/rate 必须传播并重算 | Missing | |
| CTP-V11 | SO total 必须等于复制行合计 | Missing at Convert | |
| CTP-V12 | Receipt/AR currency 必须与 SO 一致 | Missing | USD/无币种 |
| CTP-V13 | remark/delivery term 丢失必须告警 | Missing | |
| CTP-V14 | Convert 必须冻结条款版本 | Missing | 仅 quote_id 弱追溯 |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `quotes.currency` | 报价名义币种 |
| `quotes.exchange_rate` | 裸汇率快照，不进 SO |
| `quotes.validity_days` | 报价有效天数，不进 gate |
| `quotes.payment_term` | 报价付款文本，不进 SO |
| `quotes.delivery_time` | 报价交期文本，不进 SO |
| `quotes.remark` | 报价备注，不进 SO |
| `quotes.total_amount` | SO header 复制金额 |
| `quote_items.price/amount` | SO line 复制的净成交数值 |
| `quote_items.cost_price/profit_rate` | 不复制到 SO 的定价依据 |
| `sales_orders.total_amount` | 无显式币种的订单金额 |
| `sales_orders.payment_status` | 收款进度，不是 payment term |
| `customers.credit_limit/payment_days` | 客户信用预留，不作 Convert gate |
| NDE discount | 打印槽，主链通常空/零 |
| Incoterms | Quote/SO 无字段；Customs 仅 metadata |
| `receipts.currency` | 活动快捷收款固定 USD |
| `ar_records.amount/balance` | 无币种、无付款条款的应收金额 |
| `delivery_orders.total_amount` | 从 SO 复制的无显式币种金额 |
| quote_id | 唯一保留的完整报价追溯入口 |

---

## 6. State Vocabulary

| Term | Meaning / caveat |
|------|------------------|
| Draft/Sent | Quote 状态，不保证商业头完整或传播 |
| 已确认 | 已 Convert，不证明条款冻结 |
| Uncollected/Partial/Paid | SO 收款进度，不是账期 |
| Active currency/template | 元数据可用，不证明汇率有效 |
| metadata_only Incoterms | 无主商业链实现 |
| Credit Watch | 启发式展示，不是 Convert hold |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| SO 金额的正式币种应如何解释 | sales schema/services/templates、currency docs |
| 报价汇率方向、来源和日期 | quotation/defaults/currency settings、reports |
| payment term 是否有未挂载 SO 字段 | runtime migrations、sales repository/templates |
| customer payment_days/credit_limit 的正式交易门 | customer/quotation/sales/finance paths |
| special price/discount policy 的隐藏实现 | quotation/product/pricing/finance searches |
| tax-inclusive/exclusive 与 VAT 传播规则 | quote/NDE/tax/finance paths |
| Incoterm/named place 是否存在部署扩展列 | migrations/customs/quotation/sales paths |
| 报价 remark/delivery_time 丢失是否有文档补偿 | SO/NDE/DO templates/services |
| 订单/收款/AR 应采用哪个 FX 时点 | sales/finance/treasury/locale reports |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/quotation/services.py` | commercial defaults、copy 与 Quote Approve |
| `apps/quotation/repository.py` | quote header 字段持久化 |
| `v15/ux/master_defaults.py` | Zero Duplicate 默认优先级 |
| `apps/sales/services.py` | Convert header/line 传播字段 |
| `apps/sales/repository.py` | SO insert schema |
| `apps/finance/services.py` | Receipt/AR 下游边界 |
| `apps/finance/repository.py` | Receipt 与 AR 数据结构 |
| `runtime/v14/legacy_support.py` | Quote/SO/Receipt/AR schemas |
| `document/nde_engine.py` | 文档商业头、discount/incoterm 槽 |
| `templates/quote_detail.html` | Quote 商业头展示 |
| `templates/sales_order_detail.html` | SO 缺失商业头表面 |
| `business_modules/quotation.md` | Quotation 目标边界 |
| `business_modules/sales.md` | Sales 订单边界 |
| `docs/reports/V18_P6_Zero_Duplicate_Gate_Report.md` | Quote 内部头字段复用 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Convert 字段链 |
| `docs/knowledge/legacy-extract/commercial-terms/payment_terms.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/commercial-terms/commercial_incoterms.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/pricing-advanced/currency_price.md` | EAOS 只读 FX 交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后三项为 EAOS 只读交叉引用）。
