# 客户信用额度字段与来源

## Scope与证据强度

本页核验 `customers.credit_limit/credit_level/payment_days` 的 DDL、写入口、默认值与交易消费。字段存在为强结构证据；实际维护和信用 gate 缺失。概览交叉引用 [`../commercial-terms/credit_limit.md`](../commercial-terms/credit_limit.md) 与 [`../customer-deepen/ar_balance_view.md`](../customer-deepen/ar_balance_view.md)。

## 业务规则（稳定ID）

1. **CLF-R01** customers 基础 DDL 最初不含信用字段。
2. **CLF-R02** upgrade_customers 后加 credit_level、credit_limit、payment_days。
3. **CLF-R03** credit_limit 为 REAL 且无应用层默认值。
4. **CLF-R04** credit_level/payment_days 同样无活动默认值。
5. **CLF-R05** Customer Form DTO 不包含三个信用字段。
6. **CLF-R06** add/update customer repository SQL 不写三个信用字段。
7. **CLF-R07** 客户创建/编辑模板不提供额度、等级或账期输入。
8. **CLF-R08** 经营余额是 SUM(SO.total_amount)-SUM(receipts.amount)，不是 customers 持久字段。
9. **CLF-R09** Customer360 以余额绝对阈值生成 healthy/watch/risk。
10. **CLF-R10** Credit Watch/Needs Follow-up 不读取 credit_limit。
11. **CLF-R11** Customer Credit tab 的 A/B/C/D 按累计销售额，不读取 credit_level。
12. **CLF-R12** 页面使用 10k/30k/100k 多套阈值，未形成统一政策。
13. **CLF-R13** Customer360 currency 显示 USD，不证明余额经过币种折算。
14. **CLF-R14** Quote master defaults 不读取 payment_days 或 credit_limit。
15. **CLF-R15** 报价 payment_term 默认/继承链不映射 payment_days。
16. **CLF-R16** Quote Approve 不比较余额与 credit_limit。
17. **CLF-R17** Quote→SO 不读信用字段，也不传播 payment_days。
18. **CLF-R18** SO Approve、Create DO、Ship 均不读信用字段。
19. **CLF-R19** AR 主链没有 due_date，因此 payment_days 不驱动逾期。
20. **CLF-R20** DO Post AR 与 Receipt 收款形成双轨余额，但均不执行额度比较。
21. **CLF-R21** distributors 有独立 credit_limit/balance，不等于客户信用字段。
22. **CLF-R22** `validate_credit_and_pricing` 只见协作声明，未找到实现。

## 流程

1. Migration 为 customers 增加三个信用槽位。
2. 正常客户创建/编辑不填这些列。
3. Customer360 实时计算 SO−Receipt 余额。
4. 页面按固定金额阈值显示风险标签。
5. Quote 默认、批准、SO 转换、DO 与 Ship 不读取额度。
6. Payment days 不进入 AR due date 或逾期计算。
7. 因此这些字段是 schema-evolution 预留，不是可证放账控制。

## 校验（强/弱/缺失）

1. **CLF-V01（强/结构）** migration 可增加三个列。
2. **CLF-V02（强/权限）** 客户增改要求 Customers.add/edit。
3. **CLF-V03（缺失）** credit_limit 无非负、币种或上限校验。
4. **CLF-V04（缺失）** credit_level 无受控枚举。
5. **CLF-V05（缺失）** payment_days 无范围校验。
6. **CLF-V06（缺失）** 三字段无 CRUD 写入口。
7. **CLF-V07（缺失）** 余额不与额度比较。
8. **CLF-V08（缺失）** 多币种余额无 FX 转换。
9. **CLF-V09（缺失）** payment_days 不生成 due_date。
10. **CLF-V10（缺失）** Quote/SO/DO/Ship 无信用硬门禁。
11. **CLF-V11（缺失）** tenant 范围聚合未一致证明。
12. **CLF-V12（弱/UI）** 风险阈值只产生 alert。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `customers.credit_limit` | 预留授信额度槽 |
| `customers.credit_level` | 预留信用等级标签 |
| `customers.payment_days` | 预留账期天数 |
| `customer_status` | CRM 生命周期标签，不是信用冻结 |
| `customer_level` | 客户分级，与 credit level 不同 |
| Customer `balance` | SO 总额减 Receipt |
| `total_so` | 客户累计 SO 金额 |
| `total_receipt` | 客户累计收款 |
| `health=healthy/watch/risk` | 余额阈值展示 |
| `Credit Watch` | 高余额 UI 标签 |
| A/B/C/D band | 按累计销售额派生 |
| `quotes.payment_term` | 报价付款条款文本 |
| `quotes.currency` | 报价币种，不进入余额折算 |
| `ar_records.balance` | DO 级应收台账余额 |
| `receipts.currency` | 收款币种；快捷路径固定 USD |
| `receivables.due_date` | 备用结构字段，主链未使用 |
| `distributors.credit_limit` | 分销商独立额度字段 |
| `collection_tasks.balance` | 催收时经营余额快照 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Credit Watch | UI 风险提示 |
| Needs Follow-up | UI 风险提示 |
| Healthy/Watch/Risk | 余额阈值派生 |
| Credit Hold | 未实现 |
| A/B/C/D | 销售额 band，不是持久 credit_level |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| CLF-E01 | 基础 customers DDL 无信用列 | 强 | `runtime/v14/legacy_support.py` |
| CLF-E02 | upgrade_customers 增三个信用列 | 强 | `runtime/v14/legacy_support.py` |
| CLF-E03 | Customer SQL/Form 不写信用字段 | 强 | `apps/customer/repository.py`、`services.py`、`router.py` |
| CLF-E04 | 编辑模板无信用输入 | 强 | `templates/edit_customer.html` |
| CLF-E05 | Customer360 余额与风险阈值 | 强 | `apps/customer/services.py`、`templates/customer_detail.html` |
| CLF-E06 | Quote defaults 不读 credit/payment_days | 强 | `v15/ux/master_defaults.py` |
| CLF-E07 | Quote Approve 无信用比较 | 强 | `apps/quotation/services.py` |
| CLF-E08 | Convert/SO Approve 无信用读取 | 强 | `apps/sales/services.py` |
| CLF-E09 | Inventory/Ship 无信用读取 | 强 | `apps/inventory/services.py` |
| CLF-E10 | business_modules 未定义信用维护职责 | 强（缺失证据） | `business_modules/crm.md`、`finance.md` |
| CLF-E11 | A-015 明示余额启发式而非信用评分 | 强 | `docs/reports/Business_Strong_A015_Customer_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **生产库 credit_limit 是否有历史非零数据 UNKNOWN。** 已查路径：DDL、Customer SQL/Form、全库写入。
2. **是否有外部批量导入维护信用字段 UNKNOWN。** 已查路径：import/export、scripts、API、reports。
3. **payment_days 是否由隐藏任务回填 UNKNOWN。** 已查路径：master defaults、finance、migration/jobs。
4. **validate_credit_and_pricing 是否有运行时注册 UNKNOWN。** 已查路径：v15/workforce、全库函数引用。
5. **分销商额度的写入与计算规则 UNKNOWN。** 已查路径：Distributor app/template、DDL。
6. **多币种余额的基准币种 UNKNOWN。** 已查路径：Quote/SO/Receipt 字段和聚合 SQL。
7. **多租户信用敞口隔离规则 UNKNOWN。** 已查路径：tenant schema、Customer/Finance queries。
8. **credit_level 是否有合法词汇 UNKNOWN。** 已查路径：templates、locales、NDE、reports。
9. **额度审批/变更历史保存位置 UNKNOWN。** 已查路径：Approval、audit、Customer history。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
