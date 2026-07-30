# 部分清账、核销与 Write-off

## Scope 与结论

本页深化 [`../ap-payment-deepen/ap_reconcile_absence.md`](../ap-payment-deepen/ap_reconcile_absence.md)。Legacy 的 Invoice/AP 虽预留 `paid_amount`、`balance_amount`、`status`，但活动 supplier payment 路径不更新它们；未发现 allocation、partial clearing、write-off、反核销或付款冲销闭环。

## 业务规则（稳定 ID）

1. **PCW-R01** 新 Purchase Invoice 的 paid=0、balance=全额、status=Unpaid。
2. **PCW-R02** 同步 AP 的 paid=0、balance=全额、status=Unpaid。
3. **PCW-R03** AP Dashboard 直接汇总 `ap_records.amount/paid_amount/balance_amount`。
4. **PCW-R04** Supplier payment 只写 payment record 并扣 bank mirror。
5. **PCW-R05** Payment 不携带 AP/Invoice 锚点，不能定义部分核销对象。
6. **PCW-R06** 未见活动 writer 增加 AP/Invoice `paid_amount`。
7. **PCW-R07** 未见活动 writer减少 AP/Invoice `balance_amount`。
8. **PCW-R08** 未见活动 writer将 AP/Invoice 推进到 Partial/Paid/Closed。
9. **PCW-R09** 因此 AP 的“部分付款”不是可执行状态迁移。
10. **PCW-R10** 未见 payment allocation 明细表或 clearing history。
11. **PCW-R11** 未见 write-off amount/reason/date/approver 字段或实体。
12. **PCW-R12** 未见 AP debit note/credit note 用于抵销余额。
13. **PCW-R13** NDE 的 credit-note 文档模板不是 AP 会计实体，不能视为核销证据。
14. **PCW-R14** 未见 tolerance/rounding 自动尾差核销。
15. **PCW-R15** 未见 overpayment 转预付款或 unapplied credit 的数据语义。
16. **PCW-R16** `treasury_payment_records` 无 void/reversed status 与 original_payment_id。
17. **PCW-R17** 未见错误付款的反向记录或 bank balance 恢复命令。
18. **PCW-R18** 未见 clearing 与 GL/journal 分录联动。
19. **PCW-R19** 未见 supplier statement 导入后逐笔 reconcile。
20. **PCW-R20** 页面兼容显示 Partial/Paid 不证明后端有状态推进。

## 缺失的目标流程

活动代码在“付款登记并扣内部银行余额”后终止。以下环节均未观察到：

1. 选择一条或多条 AP/Invoice；
2. 将 payment 分配到每个未付余额；
3. 原子更新 AP 与 Invoice 的 paid/balance；
4. 余额大于零置 Partial，等于零置 Paid/Closed；
5. 超额保留为 unapplied/prepayment；
6. 小额差异经审批 write-off；
7. 冲销 allocation、payment 与 bank mirror；
8. 保存不可变 clearing audit trail。

## 校验（强 / 弱 / 缺失）

1. **PCW-V01（强）** Invoice/AP 创建时初始金额镜像一致。
2. **PCW-V02（强）** AP Dashboard 数值由 AP 字段直接汇总。
3. **PCW-V03（强）** 新增 payment 要求 Treasury.add。
4. **PCW-V04（弱）** UI 可展示 Unpaid/Partial/Paid 词汇。
5. **PCW-V05（弱/结构）** paid 与 balance 字段允许存储部分结果，但无活动命令。
6. **PCW-V06（缺失）** allocation amount 必须大于零。
7. **PCW-V07（缺失）** allocation≤payment 未分配余额。
8. **PCW-V08（缺失）** allocation≤AP 当前余额。
9. **PCW-V09（缺失）** clearing 前 supplier、currency、invoice 一致。
10. **PCW-V10（缺失）** `amount = paid + balance` 守恒校验。
11. **PCW-V11（缺失）** AP 与 Invoice 双镜像原子一致。
12. **PCW-V12（缺失）** write-off 原因、容差、权限与审批。
13. **PCW-V13（缺失）** closed AP 禁止再次核销。
14. **PCW-V14（缺失）** reversal 引用原记录且金额守恒。
15. **PCW-V15（缺失）** overpayment/prepayment 和汇差处理。
16. **PCW-V16（缺失）** GL 借贷平衡与会计期间关闭校验。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchase_invoices.invoice_amount` | 发票原始金额 |
| `purchase_invoices.paid_amount` | 初始化 0，付款不更新 |
| `purchase_invoices.balance_amount` | 初始化全额，付款不更新 |
| `purchase_invoices.status` | 初始化 Unpaid |
| `ap_records.amount` | AP 原始应付 |
| `ap_records.paid_amount` | 初始化 0 的镜像字段 |
| `ap_records.balance_amount` | Dashboard 应付余额字段 |
| `ap_records.status` | 初始化 Unpaid 的台账状态 |
| `treasury_payment_records.amount` | 未分配资金流出 |
| `remark` | 自由文本，非核销凭证 |
| Partial/Paid | UI/字段可表达但活动 AP 路径不推进 |
| allocation | 未建模 |
| clearing history | 未建模 |
| write-off | 未建模 |
| unapplied/prepayment | 未建模 |
| reversal/original payment | 未建模 |
| credit/debit note | AP 记账实体未发现 |
| journal entry | 与 AP clearing 联动未发现 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| PCW-E01 | Invoice/AP 初始化字段 | 强 | `apps/finance/services.py` |
| PCW-E02 | Payment 不更新 AP/Invoice | 强 | `apps/finance/services.py`、`repository.py` |
| PCW-E03 | AP 汇总直接读 AP 字段 | 强 | `apps/finance/services.py` |
| PCW-E04 | DDL 无 allocation/write-off/reversal 链 | 强 | `runtime/v14/legacy_support.py` |
| PCW-E05 | 付款表单无 clearing 对象 | 强 | `templates/payment_records.html` |
| PCW-E06 | AP 页面诚实描述人工付款 | 中/强 | `templates/ap_dashboard.html` |
| PCW-E07 | Payment360 无 clearing history | 强 | `templates/payment_record_360.html` |
| PCW-E08 | AP clearing 缺口报告 | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |
| PCW-E09 | NDE credit-note 仅文档边界 | 中 | `document/nde_engine.py`、相关 templates |

## UNKNOWN + 已查路径

1. **生产人员是否直接修改 paid/balance/status UNKNOWN。** 已查：Finance UI/API/jobs/scripts；未读生产库。
2. **旧 `accounts_payable` 结构是否有隐藏 clearing history UNKNOWN。** 已查：runtime DDL、tenant schema、repositories。
3. **供应商贷项是否在外部 ERP 维护 UNKNOWN。** 已查：credit/debit note、Finance integrations、reports。
4. **小额尾差是否由线下政策核销 UNKNOWN。** 已查：rounding/tolerance/write-off 搜索、business_modules。
5. **错误付款如何退款或冲销 UNKNOWN。** 已查：void/reverse/refund routes、services、templates。
6. **会计期间关闭与 AP 核销关系 UNKNOWN。** 已查：period/close/journal/GL 模块。
7. **多币种清账和汇差政策 UNKNOWN。** 已查：payment/AP schema、FX、Finance docs。
8. **页面中的 Partial/Paid 是否由外部任务更新 UNKNOWN。** 已查：全库 AP/Invoice UPDATE、jobs、plugins。
9. **vendor statement reconcile 是否线下执行 UNKNOWN。** 已查：supplier/finance imports、templates、reports。

## 只读来源路径

`apps/finance/`、`apps/supplier/`、`apps/approval/`、`templates/`、`runtime/v14/legacy_support.py`、`document/`、`business_modules/`、`docs/reports/`。
