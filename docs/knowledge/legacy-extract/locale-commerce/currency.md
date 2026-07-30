# 多币种与汇率（Currency / FX）— Legacy Knowledge

**Evidence strength:** Medium for currency-bearing masters/documents; weak for governed FX conversion  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 的币种语义分散在设置、品牌、国家、报价、价格试算、资金账户、文档模板等位置：

- **较强证据**：`currency_settings` 币种字典；报价头的币种与汇率快照；银行/现金账户币种；品牌默认币种。
- **中等证据**：新报价默认值优先级、报价复制时保留商业头、语言/国家驱动的币种显示。
- **弱证据**：独立价格计算器中的手输汇率及 USD 换算；多维产品价格规则结构。
- **未证实**：实时汇率提供方、汇率日期/版本、买卖价、审批、自动刷新、重估、汇兑损益和跨币种清算。

`core/capabilities/currency` 目前只有 capability 健康检查与 formatter bridge，不能视为完整币种服务。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| CUR-R1 | 币种字典以币种代码唯一标识，保存名称、符号、汇率、是否基准币、状态 | 字典结构明确；没有 ISO 长度/小数位校验 |
| CUR-R2 | 默认种子以 USD 为基准，其他种子汇率相对 USD 表达 | 价格计算器用“最终价 ÷ 汇率 = USD 价”支持这一方向；未见全局方向声明 |
| CUR-R3 | 系统设置另有 `DEFAULT_CURRENCY=USD`，品牌档案也可保存币种 | 多个默认源并存；未见单一权威主数据 |
| CUR-R4 | 新报价商业头优先复用该客户最近报价，其次品牌活动币种，最后平台 USD/1.0 | 只有最近报价能同时提供历史汇率；品牌只替换币种，平台汇率仍为 1.0 |
| CUR-R5 | 报价复制保留原报价币种与汇率 | 这是快照复制，不是按当前日期重新取价 |
| CUR-R6 | 报价行单价、成本、金额与报价头币种隐含关联 | 行本身没有明确币种字段；未见行级异币种 |
| CUR-R7 | 客户+产品历史价格只是建议，不静默覆盖人工价格 | 历史价格未做汇率归一，跨币种比较可能失真 |
| CUR-R8 | 独立价格试算先算折后价，再除以人工输入汇率得到 USD 价 | `product_id` 不参与换算；结果不保存 |
| CUR-R9 | 资金账户在创建时保存币种，期初余额直接成为当前余额 | 账户内交易未保存交易币种或汇率，隐含沿用账户币种 |
| CUR-R10 | 资金总览直接合计各账户余额 | 未按币种分组或折算；跨币种合计不具可比性 |
| CUR-R11 | 国家 profile 可建议默认币种，语言只影响显示格式 | 国家 profile 是示例型静态映射，未证实自动写入交易 |
| CUR-R12 | 币种 formatter 只做符号、代码位置与数字格式展示 | 不执行换算，也不验证币种代码 |
| CUR-R13 | 报价模板可按“报价类型+语言+币种+Active”筛选 | 模板币种是选择维度，不是汇率或金额事实 |
| CUR-R14 | 多维价格规则结构可保存国家、币种、汇率与系数 | 未发现活动匹配/生效引擎，不能迁移为已执行规则 |
| CUR-R15 | 汇率不应由 AI 或默认逻辑虚构 | 现有注释亦强调无 Fabricated FX；人工仍需确认商业头 |

---

## 3. 流程

### 3.1 新建与复制报价

1. 新建报价时先建立平台默认值：USD、汇率 1.0。
2. 若存在活动品牌币种，则替换币种。
3. 若客户有历史报价，则复用最近报价的币种和汇率等商业条件。
4. 用户可在明确的商业头更新路径调整币种/汇率。
5. 复制报价时直接复制原币种和汇率，不自动重取市场汇率。
6. 行金额按报价行单价计算；未观察到按汇率生成本位币金额。

### 3.2 独立价格试算

1. 用户输入成本、加成率、折扣率和汇率。
2. 系统得到售价和折后价。
3. 系统用折后价除以输入汇率展示 USD 价。
4. 结果仅用于页面试算，不写入报价、产品或汇率主数据。

### 3.3 资金账户

1. 创建银行或现金账户时人工输入币种与期初余额。
2. 当前余额初始化为期初余额。
3. 后续记录以账户为锚点，但支付/转账记录本身缺少币种与汇率快照。
4. 列表 KPI 直接汇总余额；没有跨币种归一过程。

### 3.4 UNKNOWN

- 汇率由谁维护、何时生效、是否需审批：**UNKNOWN**。检索 `currency_settings` 的更新路由、审计日志和权限。
- 报价转销售订单后是否完整传递币种/汇率：**UNKNOWN**。检索 `apps/quotation/` 转单路径及 sales-order schema。
- 收款、付款与发票如何处理交易币/账户币差异：**UNKNOWN**。检索 `apps/finance/`、`receipts`、`treasury_*` 的币种与汇率字段。
- 是否计算汇兑损益与期末重估：**UNKNOWN**。检索 `exchange gain/loss`、`revaluation`、`fx difference` 及会计分录表。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| CUR-V1 | 币种代码唯一 | Schema | `currency_settings.currency_code` 唯一 |
| CUR-V2 | 报价币种必填 | Hard on selected forms | 其他数据入口可能仍默认 USD |
| CUR-V3 | 汇率必须为数值 | Type-level | 报价/计算器接收浮点数 |
| CUR-V4 | 汇率必须大于零 | Missing | 试算中零会除零，负数也无商业意义 |
| CUR-V5 | 仅允许活动币种 | Missing | 表单多为自由文本，未证实绑定币种字典 |
| CUR-V6 | 恰好一个基准币 | Missing | `is_base` 没有唯一约束 |
| CUR-V7 | 基准币汇率必须为 1 | Missing | 仅种子数据如此 |
| CUR-V8 | 汇率带方向、日期、来源和版本 | Missing | 当前只有一个裸数值 |
| CUR-V9 | 历史价格比较先归一币种 | Missing | 客户历史价可跨币种混合 |
| CUR-V10 | 资金转账两端币种一致或产生 FX 明细 | Missing | 转账记录没有币种/汇率字段 |
| CUR-V11 | 金额小数位与舍入按币种定义 | Missing | 多数场景统一两位小数，不适合所有币种 |
| CUR-V12 | 国家/语言切换不得改写交易币种 | Intent only | formatter 是展示层，但端到端保护未证实 |

---

## 5. 数据含义

| Concept / Field | Legacy 含义 |
|-----------------|-------------|
| `currency_settings.currency_code` | 币种字典键；通常是 USD/CNY 等代码 |
| `currency_symbol` | 展示符号，不足以唯一识别币种 |
| `exchange_rate`（设置） | 相对基准币的配置值；方向仅由现有公式间接推断 |
| `is_base` | 基准币标记；无唯一性保证 |
| 报价头 `currency` | 报价金额的名义币种 |
| 报价头 `exchange_rate` | 报价商业头保存的汇率快照/默认值；未见本位币金额 |
| 报价行 `price/cost_price/amount` | 隐含继承报价头币种 |
| 品牌 `currency` | 公司/品牌商业默认币种候选 |
| 国家 profile `currency` | 地区展示/默认建议，不是交易事实 |
| 资金账户 `currency` | 账户余额的名义币种 |
| `opening_balance/current_balance` | 账户币金额；不可直接跨币种相加 |
| 模板 `currency` | 报价模板筛选维度 |
| formatter 输出 | 本地化字符串，只用于展示，不是换算结果 |

---

## 6. 状态词汇

| Value | Meaning / caveat |
|-------|------------------|
| `Active` | 币种、模板或品牌记录可被视为活动；不等于汇率当前有效 |
| `Inactive` / 非 `Active` | 结构上可存在，具体停用路径未证实 |
| `is_base=1` | 被标记为基准币 |
| `is_base=0` | 非基准币 |
| `Draft` | 报价草稿；币种/汇率仍可处于人工调整阶段 |
| `Sent` / `Won` / `Lost` / `Negotiating` | 报价业务状态，不代表 FX 已锁定、结算或重估 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `runtime/v14/legacy_support.py` | 币种、报价、价格规则、资金账户、品牌、模板与设置结构 |
| `v15/ux/master_defaults.py` | 新报价默认优先级及禁止虚构 FX |
| `apps/quotation/services.py` | 新建/复制报价的币种与汇率继承 |
| `apps/quotation/repository.py` | 报价商业头持久化 |
| `apps/quotation/quote_pages.py` | 模板语言/币种维度与报价入口 |
| `apps/finance/finance_ops_pages.py` | 人工汇率的 USD 价格试算 |
| `templates/product_pricing_engine.html` | 汇率输入及换算展示 |
| `apps/finance/treasury_pages.py` | 账户币种、期初/当前余额与直接汇总 |
| `core/i18n/formatter.py` | 币种展示格式，不执行换算 |
| `core/i18n/country_localization.py` | 国家与默认币种的独立维度 |
| `core/capabilities/currency/` | Currency capability 仅为 health/bridge 脚手架 |
| `docs/knowledge/legacy-extract/finance/pricing.md` | 价格公式、历史价与币种缺口交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后一项为当前 EAOS 知识包交叉引用）。
