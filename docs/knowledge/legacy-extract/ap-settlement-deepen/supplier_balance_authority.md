# 供应商余额唯一权威

## Scope 与判定

Legacy **没有可唯一解释“供应商净未付责任”的权威余额**。`SUM(ap_records.balance_amount)` 是 AP Dashboard 的应付口径；`SUM(treasury_payment_records.amount)` 是 supplier 级资金流出口径；二者无 allocation/reconcile。`suppliers` 自身也无 balance 字段。故只能分别称为“AP 台账余额”和“登记付款总额”，不能把任一单独冒充已考虑付款后的净供应商余额。

## 候选权威判定

| 候选 | 能回答 | 不能回答 | 判定 |
|---|---|---|---|
| `suppliers` | 供应商主数据 | 任何余额 | 非余额权威 |
| `purchases.total_amount` | PO 承诺金额 | 已收、已开票、已付、核销 | 非 AP 权威 |
| `purchase_invoices.balance_amount` | Invoice 初始化余额镜像 | 实际付款后余额 | 非净余额权威 |
| `ap_records.balance_amount` | AP Dashboard 当前台账口径 | 未分配付款后的净负债 | **AP 展示权威，非净结算权威** |
| payment records 按 supplier 汇总 | 登记资金流出 | 具体已清 AP、预付/退款/冲销 | 资金事实权威，非负债权威 |
| `AP balance - payments` 临时计算 | 粗略差额 | allocation、期初、预付、币种、冲销 | 禁止作为可靠权威 |

## 业务规则（稳定 ID）

1. **SBA-R01** `suppliers` 只保存身份与联系信息，没有 balance/current_balance。
2. **SBA-R02** PO 总额是采购承诺，不等于供应商应付余额。
3. **SBA-R03** Purchase Invoice 与 AP 创建时复制同一 PO 头金额。
4. **SBA-R04** Invoice 与 AP 各自保存 paid/balance/status，形成双镜像。
5. **SBA-R05** AP Dashboard 的 total AP 为全部 `ap_records.balance_amount` 求和。
6. **SBA-R06** AP Dashboard 的 total invoice/paid 也直接来自 AP，不从 Invoice/Payment 重算。
7. **SBA-R07** 部分 Treasury/Finance 风险查询只汇总 `status='Unpaid'` 的 AP balance。
8. **SBA-R08** 另一些 AP 查询不筛 status，导致报表口径内部也可能不同。
9. **SBA-R09** supplier 级 AP 可由 `GROUP BY supplier_id SUM(balance_amount)` 得出。
10. **SBA-R10** Payment records 也绑定 supplier_id，但没有 AP/Invoice 关联。
11. **SBA-R11** 付款不减少 AP 或 Invoice balance。
12. **SBA-R12** 因此付款后 `SUM(AP.balance)` 可继续保持原始全额。
13. **SBA-R13** 将 payment 简单从 AP 减除会混淆预付款、跨票分配、退款、重复和币种。
14. **SBA-R14** Bank `current_balance` 是账户资金镜像，不是 supplier balance。
15. **SBA-R15** `purchase_receipts`/inventory ledger 证明收货，不形成 supplier liability balance。
16. **SBA-R16** AP 没有到期日、币种、tenant 或 clearing history 证据足以支撑完整供应商账龄。
17. **SBA-R17** Supplier360/主数据未见按 AP+Payment 对账后的净余额字段。
18. **SBA-R18** `treasury_payment_records` 与并存 `treasury_payments` 增加资金表权威歧义。
19. **SBA-R19** 没有 supplier statement 导入与 reconciliation result 可作为第三方确认余额。
20. **SBA-R20** 重写时必须保留三种不同事实：invoice liability、payment execution、allocation/clearing。

## 校验（强 / 弱 / 缺失）

1. **SBA-V01（强）** AP Dashboard 要求 Finance.view。
2. **SBA-V02（强）** AP supplier 名称通过 supplier_id LEFT JOIN。
3. **SBA-V03（强）** 新 Invoice/AP supplier 均复制 PO supplier。
4. **SBA-V04（强）** AP 总额/已付/余额由 SQL 聚合字段。
5. **SBA-V05（强）** Treasury payment 记录 supplier_id。
6. **SBA-V06（弱）** 一 PO 应用层最多一 Invoice，降低同源重复 AP。
7. **SBA-V07（缺失）** AP 与 Invoice 双镜像一致性校验。
8. **SBA-V08（缺失）** Payment supplier 与所清 AP supplier 一致性。
9. **SBA-V09（缺失）** AP balance 自动减 payment allocation。
10. **SBA-V10（缺失）** Supplier-level debit/credit/advance 汇总守恒。
11. **SBA-V11（缺失）** 各 Dashboard 对 status filter 的统一规范。
12. **SBA-V12（缺失）** 多币种转换后的供应商基准余额。
13. **SBA-V13（缺失）** vendor statement 与内部余额调节。
14. **SBA-V14（缺失）** 余额 as-of date、会计期间与快照。
15. **SBA-V15（缺失）** 租户、删除/合并 supplier 后的完整性约束。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `suppliers.id` | supplier 主数据锚点 |
| `suppliers.supplier_code/name` | 身份信息，无余额 |
| `purchases.total_amount` | PO 头承诺金额 |
| `purchase_invoices.invoice_amount` | PO 金额快照 |
| `purchase_invoices.balance_amount` | Invoice 初始化余额镜像 |
| `ap_records.amount` | 应付原始金额 |
| `ap_records.paid_amount` | AP 已付镜像；付款不推进 |
| `ap_records.balance_amount` | AP Dashboard 的台账余额 |
| `ap_records.status` | AP 状态过滤依据 |
| `treasury_payment_records.supplier_id` | supplier 级资金归属 |
| `treasury_payment_records.amount` | 未分配付款金额 |
| `treasury_bank_accounts.current_balance` | 银行账户内部余额 |
| `inventory_ledger` PO Receipt | 收货事实，非应付余额 |
| AP supplier aggregate | supplier_id 分组的 AP 字段合计 |
| supplier payment aggregate | supplier_id 分组的资金流出 |
| net supplier liability | Legacy 无可靠单一字段/视图 |
| statement balance | 未建模 |
| as-of balance | 未建模 |

## 口径漂移示例

若 Supplier S 有一条 AP 100，随后登记 payment 60：

- AP Dashboard 仍可显示 balance 100、paid 0；
- Treasury 显示 payment 60 且 bank mirror 减 60；
- 系统没有记录这 60 是否清该 AP、是预付款还是误付；
- 人工相减得到 40 只是推测，不是可审计净余额。

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| SBA-E01 | Supplier DDL 无余额字段 | 强 | `runtime/v14/legacy_support.py` |
| SBA-E02 | Invoice/AP 双写与镜像字段 | 强 | `apps/finance/services.py` |
| SBA-E03 | AP Dashboard 聚合口径 | 强 | `apps/finance/services.py` |
| SBA-E04 | Unpaid-only 风险聚合与全量聚合并存 | 强 | `apps/finance/services.py` |
| SBA-E05 | Payment supplier 归属及无 AP FK | 强 | `apps/finance/repository.py`、DDL |
| SBA-E06 | Payment 不更新 AP/Invoice | 强 | `apps/finance/services.py`、`repository.py` |
| SBA-E07 | AP 与 payment 的页面语义 | 强 | `templates/ap_dashboard.html`、`payment_records.html` |
| SBA-E08 | AP 人工付款边界报告 | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |
| SBA-E09 | Finance 元数据/模块边界 | 中 | `core/finance/metadata.py`、`business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **业务人员当前把哪张报表当供应商对账权威 UNKNOWN。** 已查：templates、reports、business_modules。
2. **生产库是否有外部 job 回写 AP balances UNKNOWN。** 已查：jobs/scripts/plugins/integrations；未读生产库。
3. **供应商期初余额在哪里维护 UNKNOWN。** 已查：supplier/AP DDL、imports、opening balance 搜索。
4. **supplier statement 是否在线下维护 UNKNOWN。** 已查：Supplier/Finance imports、templates、reports。
5. **Invoice/AP 双镜像历史漂移程度 UNKNOWN。** 已查：writers/updates；未做生产数据剖析。
6. **多币种供应商余额换算政策 UNKNOWN。** 已查：AP/Invoice/payment schema、FX。
7. **合并或停用 supplier 后余额归属 UNKNOWN。** 已查：supplier edit/delete/merge routes。
8. **`treasury_payments` 是否含历史资金事实 UNKNOWN。** 已查：DDL、全库 writers、templates。
9. **多租户下 supplier/AP 聚合隔离是否完整 UNKNOWN。** 已查：runtime DDL、queries、tenant schemas。
10. **as-of/period-close 供应商余额如何冻结 UNKNOWN。** 已查：period/close/snapshot/journal 模块。

## 只读来源路径

`apps/finance/`、`apps/supplier/`、`apps/procurement/`、`templates/`、`runtime/v14/legacy_support.py`、`core/finance/`、`business_modules/`、`docs/reports/`。
