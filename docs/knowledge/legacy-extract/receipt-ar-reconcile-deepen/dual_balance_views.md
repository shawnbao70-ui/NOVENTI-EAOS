# Customer360 与 Statement 的双余额视图

## Scope与证据强度

本页命名并对比两套余额：View A 经营余额 `SUM(SO)-SUM(receipts)`，View B 权责台账 `SUM(ar_records.balance)`。两套查询及消费页面为强证据；自动对账、币种转换和口径披露缺失。客户侧权威交叉引用 [`../customer-deepen/ar_balance_view.md`](../customer-deepen/ar_balance_view.md)。

## 业务规则（稳定ID）

1. **DBV-R01** View A 等于客户全部 SO total_amount 减全部 receipts.amount。
2. **DBV-R02** Customer360 使用 View A。
3. **DBV-R03** 客户列表 balance 子查询也使用 View A。
4. **DBV-R04** `/ar` AR360 使用 View A。
5. **DBV-R05** `/ar_dashboard` 使用 View A 并筛正余额。
6. **DBV-R06** AR Reminder 以 View A 建 collection_tasks。
7. **DBV-R07** Customer Object360 AI 复用 legacy balance，只读且不修改。
8. **DBV-R08** View B 等于客户 ar_records.balance 汇总。
9. **DBV-R09** Statement NDE 使用 View B 的逐行 AR 与 grand total。
10. **DBV-R10** Receivable Center 显示 ar_records 行和开放余额，属于 View B。
11. **DBV-R11** Customer360 不读 ar_records。
12. **DBV-R12** Statement 不扣 receipts。
13. **DBV-R13** create_receipt 写 receipts/SO 镜像，不更新 View B。
14. **DBV-R14** DO Post AR 新增 View B，不更新 View A。
15. **DBV-R15** 同一客户可同时看到两个不同余额。
16. **DBV-R16** 只收款未 Post AR 会降低 View A，而 View B 不变。
17. **DBV-R17** 只 Post AR 未收款会增加 View B，而 View A 不变。
18. **DBV-R18** 重复 Post AR 会膨胀 View B，不影响 View A。
19. **DBV-R19** 部分发货多个 DO 可形成多条 AR；View A 仍以整张 SO 金额计。
20. **DBV-R20** Customer balance 可为负，代表超收风险但无预收分类。
21. **DBV-R21** 两视图都未做多币种折算或 currency 分组。
22. **DBV-R22** Customer360 Statement 链接从 View A 页面跳到 View B 打印，未披露口径切换。
23. **DBV-R23** `/ar` 无显式权限 gate，而 Receivable Center 要 Finance.view，用户可见口径也可能不同。

## 流程

### View A

1. 汇总客户所有 sales_orders.total_amount。
2. 汇总客户所有 receipts.amount。
3. 相减得到经营余额。
4. Customer360、客户列表、AR360、AR Dashboard 和提醒消费该值。

### View B

1. DO Post AR 为客户追加 ar_records。
2. 每行初始 amount=balance、status=Unpaid。
3. Statement/Receivable Center 读取这些静态余额。
4. Receipt 不扣减 AR 行，因此 View B 不随收款变化。

## 校验（强/弱/缺失）

1. **DBV-V01（强）** Customer360 要求客户存在。
2. **DBV-V02（强/列表）** 客户列表要求 Customers.view。
3. **DBV-V03（强）** 收款要求 Receipts.add。
4. **DBV-V04（强）** Post AR 要 Type A human confirm。
5. **DBV-V05（缺失）** 两视图没有一致性校验。
6. **DBV-V06（缺失）** Receipt 不要求分配到 ar_records。
7. **DBV-V07（缺失）** Statement 不披露未分配 receipts。
8. **DBV-V08（缺失）** 重复 Post AR 不硬阻断。
9. **DBV-V09（缺失）** 多币种金额直接相加。
10. **DBV-V10（缺失）** 负 View A 不分类预收/退款。
11. **DBV-V11（缺失）** View B balance 无自动更新。
12. **DBV-V12（缺失）** SO 镜像与 receipts SUM 也无后台 reconciliation。
13. **DBV-V13（缺失）** Statement 未标明与 Customer360 公式不同。
14. **DBV-V14（弱/权限不对称）** `/ar` 与 Receivable Center 权限不同。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `total_so` | 客户全部 SO 金额 |
| `total_receipt` | 客户全部 receipts 金额 |
| Customer `balance` | total_so-total_receipt |
| `sales_orders.received_amount` | SO 收款镜像 |
| `sales_orders.balance_amount` | SO 剩余镜像 |
| `payment_status` | SO 付款进度 |
| `receipts.customer_id` | View A 的收款汇总键 |
| `receipts.so_id` | 收款对应 SO |
| `ar_records.amount` | DO Post AR 原始应收 |
| `ar_records.balance` | View B 行余额 |
| `ar_records.source_no` | 来源 DO 号 |
| `ar_records.status` | Unpaid/Closed 等台账词汇 |
| Statement `grand_total` | ar_records.balance 总和 |
| `statement_lines` | ar_records 逐行开放项 |
| `collection_tasks.balance` | View A 的提醒快照 |
| negative balance | 超收结果，未分类 |
| `currency='USD'` | 展示/收款默认，不是折算基币证明 |
| `receivables` | 并行遗留表，非两视图主源 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Clear/Paid | View A 余额已清 |
| Partial | View A 部分收款 |
| Unpaid | AR 行初始状态或经营未收 |
| Closed | View B 排除词汇，写入口未找到 |
| Outstanding | 可能指 View A 或 View B，必须看页面 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| DBV-E01 | Customer360 View A 公式 | 强 | `apps/customer/services.py` |
| DBV-E02 | 客户列表 View A 子查询 | 强 | `apps/customer/repository.py` |
| DBV-E03 | `/ar` 和 AR Dashboard 使用 View A | 强 | `apps/finance/services.py`、`repository.py` |
| DBV-E04 | 收款只写 receipts/SO 镜像 | 强 | `apps/finance/services.py`、`repository.py` |
| DBV-E05 | DO Post AR 写 View B | 强 | `apps/inventory/services.py`、`apps/finance/services.py` |
| DBV-E06 | Statement 从 ar_records 构造 | 强 | `document/nde_engine.py`、`templates/documents/statement.html` |
| DBV-E07 | Receivable Center 显示 ar_records.balance | 强 | `templates/receivable_center.html` |
| DBV-E08 | Customer 页面从 View A 链到 Statement | 强 | `templates/customer_detail.html` |
| DBV-E09 | AR 路由权限不对称 | 强 | `apps/finance/router.py` |
| DBV-E10 | A-011 记录 AR 页面口径和诚实性缺口 | 强 | `docs/reports/Business_Strong_A011_AR_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **Statement 是否应并列披露两套余额 UNKNOWN。** 已查路径：customer_detail、statement template、NDE engine。
2. **是否存在 View A↔View B 同步 job UNKNOWN。** 已查路径：apps、scripts、scheduler、reports。
3. **Receipt 撤销如何恢复 View A/SO 镜像 UNKNOWN。** 已查路径：Finance routes/services、templates。
4. **ar_records.balance 何时关闭 UNKNOWN。** 已查路径：UPDATE ar_records、triggers、jobs。
5. **多币种客户余额的基准币种 UNKNOWN。** 已查路径：Receipt currency、SO/Quote currency、聚合 SQL。
6. **receivables 与 ar_records 谁是会计权威 UNKNOWN。** 已查路径：DDL、Finance services、business_modules。
7. **tenant scope 是否一致 UNKNOWN。** 已查路径：Customer utils/repository、Finance queries。
8. **SO 无 DO 时是否应产生 AR UNKNOWN。** 已查路径：Sales、Inventory DO invoice、Finance。
9. **负余额应作为预收、退款还是贷项 UNKNOWN。** 已查路径：Treasury、receipts、credit note。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
