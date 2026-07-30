# 转单商务条款快照清单（Term Snapshot on Convert）— Legacy Knowledge

**Evidence strength:** Strong for source/target columns and Convert inserts; strong negative for a governed full commercial snapshot  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页以字段清单方式核对付款、信用、FX、折扣、Incoterms、税、有效期、交期和备注在 Convert 时是“显式快照、净结果隐含、仅保留源引用、缺失或平行链”。结论是 Convert 冻结金额与行成交结果，不冻结完整商务契约。

交叉引用 `../quote-convert-policy-deepen/commercial_term_propagation.md`、`../commercial-terms/**` 和 `../pricing-advanced/**`。

## 2. Snapshot Classification

| Classification | Meaning |
|----------------|---------|
| Explicit snapshot | 目标 SO/line 有明确列并复制值 |
| Implicit result | 只复制计算后金额，不保留规则/基准 |
| Source-only | 值仍在 Quote/Customer，可经 quote_id 回查 |
| Missing | 主链无可用字段或未传播 |
| Parallel | 仅 GFIP/Customs/Pricing 等独立能力存在 |

## 3. Business Rules

| ID | Rule / observed boundary | Classification |
|----|--------------------------|----------------|
| TS-R1 | SO 保存 quote_id | Explicit trace reference |
| TS-R2 | SO 复制 customer_id/salesperson_id | Explicit party assignment |
| TS-R3 | SO order_date 复制 quote_date | Explicit，但不是 Convert timestamp |
| TS-R4 | SO total_amount 复制 quote total | Explicit monetary result |
| TS-R5 | SO lines 复制 product/qty/price/amount | Explicit line result |
| TS-R6 | Quote currency 不进入 SO | Source-only |
| TS-R7 | Quote exchange_rate 不进入 SO | Source-only |
| TS-R8 | SO 金额无 document currency 列 | Missing semantic |
| TS-R9 | payment_term 不进入 SO | Source-only |
| TS-R10 | customer payment_days 不冻结 | Source-only |
| TS-R11 | credit_limit/credit_level 不冻结也不 gate | Source-only |
| TS-R12 | validity_days 不冻结且不过期校验 | Source-only |
| TS-R13 | delivery_time 不进入 SO | Source-only |
| TS-R14 | quote remark 不进入 SO | Source-only |
| TS-R15 | cost/profit/profit_rate 不进入 SO line | Source-only |
| TS-R16 | 折扣字段不在 Quote/SO 主 line model | Missing；price 是净结果 |
| TS-R17 | special price/rule ID 不随 line 传播 | Missing |
| TS-R18 | Quote/SO 无 Incoterm/named place 主字段 | Missing |
| TS-R19 | Customs registry/GFIP Incoterm 与主链平行 | Parallel |
| TS-R20 | Quote/SO 主链未形成 tax mode/rate/amount snapshot | Missing |
| TS-R21 | NDE discount/tax/incoterm slots 不等于持久事实 | Presentation only |
| TS-R22 | SO 初始 payment_status 是收款进度 | 不等于付款条款 |
| TS-R23 | Receipt 快捷路径固定 USD | 不继承 Quote FX |
| TS-R24 | AR 金额无 currency/due date | 商务快照继续断裂 |
| TS-R25 | quote_id 是回查源条款的唯一宽引用 | 不等于不可变 snapshot |
| TS-R26 | Quote 后续可变更时 SO 不保留 Convert 时条款版本 | 无时间点证据 |
| TS-R27 | EAOS 不得把金额复制称为合同条款复制 | 只证明结果快照 |

## 4. Field Snapshot Matrix

| Term / field | Quote/Customer source | Convert→SO | Downstream consequence | Class |
|--------------|-----------------------|------------|------------------------|-------|
| quote_id | quotes.id | `sales_orders.quote_id` | 可回查当前 Quote | Explicit trace |
| customer | quotes.customer_id | customer_id | DO/AR party 来源 | Explicit |
| salesperson | quotes.salesperson_id | salesperson_id | TC 归属来源 | Explicit |
| quote date | quotes.quote_date | order_date | 非实际转换时间 | Explicit |
| total | quotes.total_amount | total_amount | DO/Receipt 基数 | Explicit |
| line product/qty/price/amount | quote_items | SO items | 净成交结果 | Explicit |
| currency | quotes.currency | 不复制 | SO amount 币种不明 | Source-only |
| exchange rate | quotes.exchange_rate | 不复制 | 无本位币/FX snapshot | Source-only |
| validity | quotes.validity_days | 不复制/不 gate | 过期仍可转 | Source-only |
| payment term | quotes.payment_term | 不复制 | payment_status 不能替代 | Source-only |
| payment days | customers.payment_days | 不读取 | AR 无 due date | Source-only |
| credit limit/level | customers | 不读取 | 无 convert hold | Source-only |
| delivery time | quotes.delivery_time | 不复制 | DO 无承诺快照 | Source-only |
| remark | quotes.remark | 不复制 | SO 不保留报价备注 | Source-only |
| line cost/profit | quote_items | 不复制 | SO 毛利用产品当前成本重算 | Source-only |
| discount | 无主链列/打印槽 | 不复制 | 只有净价 | Missing/implicit |
| price rule/version | 平行/预留 | 不复制 | 无可解释性 | Missing |
| Incoterm/named place | 主 Quote 无字段 | 不复制 | GFIP 可能默认 FOB | Missing/parallel |
| tax mode/rate/amount | 未形成主链合同 | 不复制 | Finance tax 独立 | Missing/parallel |
| commission rule | salesperson level | TC 快照，不在 SO | 与合同条款分离 | Side effect |

## 5. Process

1. Quote 形成商业头与价格结果。
2. Approve 可改 qty/price，但不建立条款版本对象。
3. Convert 读取当前 quote，复制五类 header/line 结果。
4. quote_id 保留对源的弱追溯。
5. TC 另存费率/金额快照。
6. SO/DO/Receipt/AR 不自动补齐 currency、term、credit、Incoterm、tax。
7. NDE 可从 Quote 读取部分条款用于打印；不反向证明 SO 已冻结。

## 6. Validation

| ID | Validation | Strength |
|----|------------|----------|
| TS-V1 | quote 存在且无 SO | Hard |
| TS-V2 | quote 商业头完整才可 Convert | Missing |
| TS-V3 | validity 未过期 | Missing |
| TS-V4 | currency active 且 rate>0 | Missing |
| TS-V5 | SO 必须保存 currency/FX snapshot | Missing |
| TS-V6 | payment term/days 必须传播 | Missing |
| TS-V7 | credit exposure 必须校验并冻结 | Missing |
| TS-V8 | discount/rule/version 必须保存 | Missing |
| TS-V9 | Incoterm + named place 必须保存 | Missing |
| TS-V10 | tax mode/rate/amount 必须保存 | Missing |
| TS-V11 | copied header total 等于 copied lines | Missing at Convert |
| TS-V12 | terms 必须关联不可变 version/hash | Missing |
| TS-V13 | Receipt/AR currency 必须与订单一致 | Missing |
| TS-V14 | source Quote 变更后必须保留原快照 | Missing |

## 7. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `sales_orders.quote_id` | 对源 Quote 的动态回查链接 |
| `order_date` | quote date 副本 |
| `total_amount` | 无显式币种的金额副本 |
| SO line price | Quote 净成交单价副本 |
| SO line amount | Quote 行金额副本 |
| `quotes.currency` | 留在源 Quote 的名义币种 |
| `quotes.exchange_rate` | 留在源 Quote 的裸快照 |
| `quotes.payment_term` | 留在源 Quote 的付款文本 |
| `customers.payment_days` | 未冻结的当前客户字段 |
| `customers.credit_limit` | 未进入 gate 的当前客户字段 |
| `quotes.validity_days` | 未消费的有效期 |
| `quotes.delivery_time` | 未复制的交期文本 |
| `quotes.remark` | 未复制的备注 |
| net price | 折扣/规则依据缺失后的结果数值 |
| NDE discount/incoterm/tax | 展示槽，不是 SO persistent fact |
| `sales_orders.payment_status` | 收款进度，不是付款条件 |
| `receipts.currency` | 快捷收款 USD 默认 |
| `ar_records.amount/balance` | 无币种/账期的应收 |
| `tc_ledger.commission_rate` | 独立副作用中的费率快照 |
| term version/hash | 未建模 |

## 8. State Vocabulary

| Term | Meaning |
|------|---------|
| explicit snapshot | Convert 目标列有值 |
| source-only | 只能经 quote_id/customer 回查 |
| implicit net result | 有金额，无折扣/定价依据 |
| missing | 主链没有字段/传播 |
| parallel | 独立模块存在但未接 Convert |
| `已确认` | Convert 已执行，不证明条款冻结 |
| Uncollected/Partial/Paid | 收款状态，不是账期 |

## 9. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| SO amount 正式币种解释 | Sales DDL/repository/templates、Finance |
| 生产 SO 是否有私有商业头扩展列 | runtime/database migrations |
| Quote 在 Convert 后是否仍可改商业头 | quotation update routes/templates |
| 条款版本/hash 是否存在隐藏表 | quotation/document/contracts/reports |
| special price/discount rule 的生产来源 | quotation/product/pricing/finance |
| tax inclusive/exclusive 的正式计算次序 | NDE/tax/finance/quotation |
| customer credit 的正式 Convert gate | customer/sales/finance |
| Incoterm 是否存在部署扩展与 named place | customs/GFIP/migrations |
| SO/DO print 是否动态 join Quote 补条款 | print center/NDE/templates |
| FX 应在 quote/order/invoice/receipt 哪一时点冻结 | quotation/sales/finance/treasury |

## 10. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/quotation/repository.py` | Quote 商业头与行字段 |
| `apps/quotation/services.py` | defaults/Approve/print |
| `v15/ux/master_defaults.py` | 商业头默认来源 |
| `apps/sales/services.py` | Convert 字段复制清单 |
| `apps/sales/repository.py` | SO/line insert 列 |
| `runtime/v14/legacy_support.py` | Quote/SO/Receipt/AR schemas |
| `apps/finance/services.py` | Receipt USD 与 AR 下游 |
| `apps/finance/repository.py` | 财务字段消费 |
| `document/nde_engine.py` | 打印商业头和空槽 |
| `templates/quote_detail.html` | Quote 条款展示 |
| `templates/sales_order_detail.html` | SO 条款缺失表面 |
| `apps/customs_center/incoterm_registry.py` | Incoterm 平行 registry |
| `v15/gfip/` | 平行贸易链默认/文档 |
| `business_modules/quotation.md` | Quote 边界 |
| `business_modules/sales.md` | SO authority |
| `docs/reports/V18_P6_Zero_Duplicate_Gate_Report.md` | Quote 内商业头复用 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Convert 字段链 |
| `docs/knowledge/legacy-extract/quote-convert-policy-deepen/commercial_term_propagation.md` | EAOS 只读传播交叉引用 |
| `docs/knowledge/legacy-extract/commercial-terms/payment_terms.md` | EAOS 付款条款交叉引用 |
| `docs/knowledge/legacy-extract/commercial-terms/credit_limit.md` | EAOS 信用交叉引用 |
| `docs/knowledge/legacy-extract/commercial-terms/commercial_incoterms.md` | EAOS Incoterms 交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后四项为 EAOS 只读交叉引用）。
