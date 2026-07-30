# 税务（Tax）— Legacy Knowledge

**Evidence strength:** Medium for tax metadata/registry; weak for transactional tax calculation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

Legacy 中可见两类不等价的税务数据：

1. **税率设置 `tax_settings`**：按税码、税名、国家、税率和状态保存税务字典；
2. **税务记录 `tax_records`**：按税号、税种、日期、金额、状态和备注保存独立台账。

`/tax_center` 只读取税务记录；活动示例路径直接插入一条固定 VAT 记录。未观察到报价、销售订单、采购、发票或收付款依据 `tax_settings` 自动计算税额，也未观察到含税价/未税价拆分、进销项抵扣、申报期或总账过账。

`core/capabilities/tax` 目前只有 capability 健康检查与 country-localization bridge，不能视为税务引擎。

---

## 2. 业务规则

| ID | 规则描述 | 证据 / 缺口 |
|----|----------|-------------|
| TAX-R1 | 税率设置以税码唯一标识，并关联国家代码、百分比税率和活动状态 | 主数据结构明确 |
| TAX-R2 | 初始税率包含多个国家的 VAT/PPN 种子 | 种子是静态配置；不可据此认定当前法定税率 |
| TAX-R3 | 税务记录以独立税号记录税种、日期、金额、状态和备注 | 没有 taxable base、rate、currency、party 或 source document |
| TAX-R4 | 税务中心按最新 ID 倒序展示税务记录 | 只读列表，没有汇总/申报计算证据 |
| TAX-R5 | 示例新增路径写入固定 VAT、固定金额和 `Pending` 状态 | 不是从业务单据或税率字典计算，且 GET 触发写入 |
| TAX-R6 | `tax_settings` 与 `tax_records` 没有可观察到的外键或税码关联 | 税务记录的 `tax_type` 只是自由文本 |
| TAX-R7 | 报价行价格公式只计算成本、售价、利润和金额 | 未见税率、税额、含税标记或价税合计 |
| TAX-R8 | 独立定价试算只处理成本、加成、折扣与汇率 | “最终价”不能推定为含税或未税 |
| TAX-R9 | 国家与语言是独立维度；国家 profile 可承载税务上下文意图 | 静态 country profile 未自动驱动交易税率 |
| TAX-R10 | UI 翻译可以本地化税务标签，但不得翻译或改变税码、税率与金额事实 | 未观察到端到端税务表单本地化校验 |
| TAX-R11 | 税务金额不能从 `tax_records.amount` 反推税基或税率 | 缺少组成字段 |
| TAX-R12 | 不应把 capability scaffold、设置表或 Tax Center 列表称为税务自动化 | 只有 health/metadata/registry 证据 |

---

## 3. 流程

### 3.1 税率设置

1. 启动初始化 `tax_settings` 表。
2. 以 `INSERT OR IGNORE` 写入预置国家税率。
3. 记录可带 `Active` 状态、备注及创建/更新时间。
4. 未发现活动交易在报价/采购/发票计算时匹配该表。

### 3.2 税务台账

1. Tax Center 查询 `tax_records` 并按 ID 倒序显示。
2. 页面按 `Pending` 与其他状态使用不同徽标。
3. 活动示例入口插入固定税号、VAT、当天日期、固定金额和备注。
4. 记录创建后没有可确认的审核、完成、申报、付款或会计过账流程。

### 3.3 与价格/单据交界

1. 产品和报价链形成成本、售价、折扣、利润及报价总额。
2. 当前公式未引入税码或税率。
3. 报价/订单/采购/发票字段中未确认统一的 `tax_inclusive`、`tax_amount`、`net_amount`、`gross_amount` 语义。
4. 因此报价总额不能诚实地解释为含税或未税金额。

### 3.4 UNKNOWN

- 税率生效期、版本和法规来源：**UNKNOWN**。检索 `tax_settings` 更新历史、effective date、jurisdiction/version。
- 客户/供应商税号与免税资格如何选择税率：**UNKNOWN**。检索 party master 的 `tax_number`、exemption、registration 与交易匹配逻辑。
- 销项税、进项税、预提税、关税和复合税如何处理：**UNKNOWN**。检索报价、采购、发票、报关及总账分录。
- `tax_records.amount` 是应纳税额、已缴税额、申报额还是手工事项金额：**UNKNOWN**。检索 Tax Center 写入/更新路径和报表。
- 含税价反算、折扣与税的先后顺序、舍入层级：**UNKNOWN**。检索 line/header tax 公式与测试。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| TAX-V1 | 税码唯一 | Schema | `tax_settings.tax_code` 唯一 |
| TAX-V2 | 国家代码必须有效 | Missing | 未见与 countries 表的外键 |
| TAX-V3 | 税率必须处于合理区间 | Missing | 未见 0–100 或负税率规则 |
| TAX-V4 | 同国同税种生效期不可重叠 | Not modeled | 没有生效起止日期 |
| TAX-V5 | 税务记录必须引用来源单据和主体 | Missing | 当前结构无来源键/party 键 |
| TAX-V6 | 税务记录币种明确 | Missing | `tax_records` 无 currency |
| TAX-V7 | 税额等于税基乘税率并按规则舍入 | Missing | 无税基、税率快照或公式 |
| TAX-V8 | 含税/未税标记明确 | Missing | 价格及单据没有统一语义 |
| TAX-V9 | 状态迁移受权限与审计控制 | Not evidenced | 只看到列表和测试写入 |
| TAX-V10 | 修改操作使用非 GET 方法 | Violated | `/add_test_tax` 通过 GET 写入 |
| TAX-V11 | 静态种子税率在使用前经业务确认 | Missing | 无法证明法规时效性 |
| TAX-V12 | 税码/税率不因 UI 语言改变 | Intent only | 本地化层与业务事实应分离 |

---

## 5. 数据含义

| Concept / Field | Legacy 含义 |
|-----------------|-------------|
| `tax_settings.tax_code` | 税率主数据键，如国家+税种组合 |
| `tax_name` | 税种显示名称 |
| `country_code` | 税务国家/地区代码；无外键保证 |
| `tax_rate` | 百分比配置值，不带生效期或版本 |
| `tax_settings.status` | 主数据是否活动，不代表法规有效性已验证 |
| `tax_records.tax_no` | 税务事项编号 |
| `tax_records.tax_type` | 自由文本税种；未绑定 `tax_code` |
| `tax_date` | 税务记录日期；不是明确的税期/申报期 |
| `amount` | 未定义组成的税务金额 |
| `tax_records.status` | 台账状态；活动页面仅特判 `Pending` |
| `remark` | 人工备注 |
| 报价 `total_amount` | 报价行金额合计；含税属性未定义 |
| 定价 `final_price` | 加成和折扣后的试算价；不能推定含税 |

---

## 6. 状态词汇

| Value | Meaning / caveat |
|-------|------------------|
| `Active` | 税率设置可用/活动；不证明当前法定有效 |
| `Inactive` / 非 `Active` | 可能表示停用；未见完整维护路径 |
| `Pending` | 税务记录待处理；没有明确后续状态机 |
| `Completed` | 页面把所有非 `Pending` 值展示成完成风格，可能掩盖未知/错误状态 |
| `VAT` | 示例税种文本，不是与 `tax_settings` 绑定的税码 |
| `PPN` | 印尼种子税名的一部分；仅主数据语义 |

---

## 7. 只读来源路径

| Path | Why cited |
|------|-----------|
| `runtime/v14/legacy_support.py` | `tax_settings`、`tax_records` 结构与种子税率 |
| `apps/finance/finance_ops_pages.py` | Tax Center 查询和固定测试记录写入 |
| `templates/tax_center.html` | 税务台账展示与状态分支 |
| `apps/quotation/services.py` | 报价金额/利润流程无税务计算 |
| `apps/quotation/repository.py` | 报价头/行持久化语义 |
| `templates/product_pricing_engine.html` | 试算公式不含税 |
| `core/i18n/country_localization.py` | 国家与语言独立、国家商务属性意图 |
| `core/capabilities/tax/` | Tax capability 仅为 health/bridge 脚手架 |
| `docs/reports/audit/07_I18N_AUDIT.md` | 税务能力被标记为设置/记录加 scaffold |
| `docs/knowledge/legacy-extract/finance/pricing.md` | 价格公式、金额与校验缺口交叉引用 |
| `docs/knowledge/legacy-extract/finance/invoices.md` | 发票语义与实现缺口交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为当前 EAOS 知识包交叉引用）。
