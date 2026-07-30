# AP 勾兑、核销与对账缺口

## Scope与证据强度

本页记录 AP payment allocation、settlement、partial clearing、三单匹配、供应商对账与银行对账的缺失。缺失结论来自表结构、写入路径和报告交叉检索；不把目标能力描述成 Legacy 行为。

## 业务规则（稳定ID）

1. **ARA-R01** AP 仅随采购发票初始化为 Unpaid。
2. **ARA-R02** Treasury payment 只绑定 supplier_id 和 bank account。
3. **ARA-R03** Payment 无 ap_id/invoice_id。
4. **ARA-R04** 无 payment allocation 明细实体。
5. **ARA-R05** 付款不更新 ap_records。
6. **ARA-R06** 付款不更新 purchase_invoices。
7. **ARA-R07** 无 AP partial payment 状态迁移。
8. **ARA-R08** 无 Paid/Closed 自动判定。
9. **ARA-R09** 未分配付款只能作为 supplier-level 资金事实存在。
10. **ARA-R10** 无 AP write-off 或 debit/credit note 核销实体。
11. **ARA-R11** NDE credit note 是文档模板，不是 AP 记账实体。
12. **ARA-R12** 无 vendor statement 导入/匹配。
13. **ARA-R13** bank_transactions 有 DDL 但未见活动写入。
14. **ARA-R14** 无银行流水与 payment records 对账作业。
15. **ARA-R15** purchase_receipts 无活动写入。
16. **ARA-R16** Invoice 不引用结构化 GR。
17. **ARA-R17** 无 PO/GR/Invoice 三单匹配。
18. **ARA-R18** 无匹配容差、差异审批或 price/qty variance。
19. **ARA-R19** 付款无 Approval Center 联动。
20. **ARA-R20** 付款无专用 write_log/audit。
21. **ARA-R21** AR 收款至少关联 SO；AP 付款没有对称锚点。
22. **ARA-R22** A-020 验收保证 UI 诚实，不代表核销已实现。

## 流程

实际流程分叉：

1. PO→Invoice→AP 写入静态 Unpaid 应付。
2. Supplier→Payment Record→Bank Balance 写入资金流出。
3. 两条链没有 allocation/clearing 汇合点。
4. GR 只落 Inventory Ledger，不进入三单匹配。
5. 所以 AP Dashboard 保持原始余额，付款后仍可能显示全额未付。

## 校验（强/弱/缺失）

1. **ARA-V01（强）** 创建 invoice 前 PO 存在。
2. **ARA-V02（强）** 同 PO 发票 service 查重。
3. **ARA-V03（强）** 付款需要 Treasury.add。
4. **ARA-V04（缺失）** 付款必须选择 AP/Invoice。
5. **ARA-V05（缺失）** allocation 总额≤payment。
6. **ARA-V06（缺失）** allocation 总额≤AP balance。
7. **ARA-V07（缺失）** partial 后重算 paid/balance/status。
8. **ARA-V08（缺失）** fully paid 后关闭 AP。
9. **ARA-V09（缺失）** write-off/credit adjustment 审批。
10. **ARA-V10（缺失）** vendor statement 匹配。
11. **ARA-V11（缺失）** bank transaction 匹配。
12. **ARA-V12（缺失）** PO/GR/Invoice 三单数量金额校验。
13. **ARA-V13（缺失）** 付款多币种/汇差校验。
14. **ARA-V14（缺失）** reconcile 冲销/反核销。
15. **ARA-V15（缺失）** 付款服务端审批和审计。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `ap_records.amount` | 静态原始应付 |
| `ap_records.paid_amount` | 初始 0，未被付款更新 |
| `ap_records.balance_amount` | Dashboard 静态余额 |
| `ap_records.status` | 初始 Unpaid |
| `purchase_invoices.balance_amount` | 发票侧静态余额 |
| `treasury_payment_records.supplier_id` | 供应商级付款归属 |
| `treasury_payment_records.amount` | 未分配资金流出 |
| `account_id` | 内部银行账户 |
| `current_balance` | 付款后扣减的银行镜像 |
| `purchase_receipts` | 未使用的 GR DDL |
| `inventory_ledger PO Receipt` | 实际收货事实 |
| `bank_transactions` | 无活动 writer 的银行交易表 |
| payment allocation | 未建模 |
| unapplied payment | 无专用状态，事实性存在 |
| vendor statement | 未建模 |
| write-off | 未建模 |
| match variance | 未建模 |
| `receipts.so_id` | AR 有、AP 无的分配锚点 |

## 状态词汇

| 词汇 | 实际语义 |
|---|---|
| Unpaid | AP 初始化状态 |
| Partial/Paid | UI 兼容，AP 无活动推进 |
| Allocated/Cleared/Settled | 未实现 |
| Unapplied | 无字段，但付款未分配 |
| Reconciled/Matched | 未实现 |
| Written Off/Reversed | 未实现 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| ARA-E01 | AP/Invoice/Payment/Bank DDL 无 allocation FK | 强 | `runtime/v14/legacy_support.py` |
| ARA-E02 | 发票+AP 仅初始化 | 强 | `apps/finance/services.py` |
| ARA-E03 | 付款仅写流水并扣银行 | 强 | `apps/finance/services.py`、`repository.py` |
| ARA-E04 | 付款表单无 AP/Invoice | 强 | `templates/payment_records.html` |
| ARA-E05 | 收货不写 purchase_receipts | 强 | `apps/procurement/services.py` |
| ARA-E06 | 三单匹配正式列为 gap | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| ARA-E07 | A-020 只做 UI 诚实性 gate | 强 | `scripts/business_strong_a020_ap_ops_gate.py`、对应报告 |
| ARA-E08 | Finance 元数据无 allocation 表 | 强 | `core/finance/metadata.py` |
| ARA-E09 | AR receipt 有 so_id 对照 | 强 | `apps/finance/services.py`、`runtime/v14/legacy_support.py` |

## UNKNOWN + 已查路径

1. **生产库是否有人工作业直接改 AP UNKNOWN。** 已查路径：UI/API/jobs/scripts；未读生产 DB。
2. **accounts_payable 旧表是否含 allocation UNKNOWN。** 已查路径：DDL、tenant schema、repositories。
3. **bank_transactions 是否由外部导入 UNKNOWN。** 已查路径：Finance imports、writers、reports。
4. **供应商对账单是否在线下维护 UNKNOWN。** 已查路径：Supplier/Finance templates、imports。
5. **信用票/贷项是否在外部 ERP 处理 UNKNOWN。** 已查路径：credit note、NDE、Finance entities。
6. **三单匹配是否由人工完成 UNKNOWN。** 已查路径：business_modules、reports、Approval。
7. **付款审批是否由组织流程替代 UNKNOWN。** 已查路径：Approval app、payment handlers。
8. **多币种未分配付款处理 UNKNOWN。** 已查路径：Payment schema、bank currency、FX。
9. **银行对账是否有未入库插件 UNKNOWN。** 已查路径：plugins/integrations/bank transaction writers。
10. **重复 payment handlers 的运行优先级 UNKNOWN。** 已查路径：router、treasury_pages、bootstrap。
11. **生产 purchase_receipts 是否有历史数据 UNKNOWN。** 已查路径：DDL/writers；未查询 live DB。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\approval\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
