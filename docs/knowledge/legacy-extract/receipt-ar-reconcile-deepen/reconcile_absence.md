# 收款勾兑、核销与分配缺失

## Scope与证据强度

本页核验 payment allocation、receipt-to-AR matching、reconciliation、write-off 和自动核销作业。最强事实是收款成功后没有 `UPDATE ar_records`；`receipt_items` 仅有只读 JOIN 痕迹，无 DDL/写入。既有结论交叉引用 [`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)。

## 业务规则（稳定ID）

1. **REC-R01** 收款唯一活动入口按 so_id 创建 receipts。
2. **REC-R02** 收款金额是 SO 剩余全额，不是用户分配金额。
3. **REC-R03** receipts 没有 ar_record_id。
4. **REC-R04** 收款成功只更新 SO 收款镜像。
5. **REC-R05** 收款不读取或更新 ar_records。
6. **REC-R06** DO Post AR 只 INSERT Unpaid ar_records。
7. **REC-R07** ar_records.source_no 是 DO 号，不是可勾兑外键。
8. **REC-R08** ar_records.balance 创建后未找到递减写入口。
9. **REC-R09** ar_records.status 未找到 Partial/Paid/Closed 写入口。
10. **REC-R10** 未找到 receipt allocation 主表或子表。
11. **REC-R11** receipt_items 只在 context360 只读 JOIN 中出现。
12. **REC-R12** 未找到 receipt_items DDL 或 INSERT。
13. **REC-R13** collections/receivables 有遗留 DDL，但无当前收款/核销写入。
14. **REC-R14** collection_tasks 是催收任务，不是金额分配。
15. **REC-R15** Statement 只读 ar_records，不展示 receipts 分配。
16. **REC-R16** AR360 读 SO−receipts，不读 AR allocation。
17. **REC-R17** Receivable Center 读 ar_records 静态余额。
18. **REC-R18** 未找到 reconcile/match/allocation/write-off scheduler 或 batch。
19. **REC-R19** 同 DO 重复 Post 只 warning，会放大未勾兑 AR。
20. **REC-R20** SO Paid 可以与 ar_records Unpaid 同时存在。
21. **REC-R21** 多 DO 对一 SO 时无法把一笔 receipt 分配到各 AR 行。
22. **REC-R22** 超收只在 SO 余额层截零，不形成预收/贷项/退款分配。
23. **REC-R23** 未见 receipt void 后恢复 SO 与 AR 的冲销流程。
24. **REC-R24** treasury_payment_records 是 AP 出款，不是客户 AR 核销。
25. **REC-R25** business_modules 声明的 payments/accounts_receivable 与运行时 receipts/ar_records 不一致。

## 流程

### 实际并行链

1. SO 快捷收款写 receipts。
2. Finance 更新 SO received/balance/payment_status。
3. DO Post AR 独立插入 ar_records。
4. Statement/Receivable Center继续显示原始 AR balance。
5. 系统没有把 receipt 金额分配到某一或多条 AR。

### 缺失的勾兑链

未发现：选择 receipt→选择 open AR→输入 allocation→校验分配总额→扣减 balance→更新 Partial/Paid/Closed→写 reconciliation history→处理差额/write-off。

## 校验（强/弱/缺失）

1. **REC-V01（强）** 收款前 SO 必须存在。
2. **REC-V02（强）** SO 剩余必须大于 0 才插 receipt。
3. **REC-V03（强/权限）** 收款要求 Receipts.add。
4. **REC-V04（强）** DO Post AR 要 human_confirm。
5. **REC-V05（缺失）** 同 DO 不得重复 AR 未硬校验。
6. **REC-V06（缺失）** Receipt 不要求关联任何 AR。
7. **REC-V07（缺失）** allocation 合计不超过 receipt amount 未实现。
8. **REC-V08（缺失）** allocation 不超过 AR balance 未实现。
9. **REC-V09（缺失）** Receipt 与 AR 客户一致性未实现。
10. **REC-V10（缺失）** Closed AR 不可再核销未实现。
11. **REC-V11（缺失）** 部分核销更新 Partial 未实现。
12. **REC-V12（缺失）** 全额核销更新 Paid/Closed 未实现。
13. **REC-V13（缺失）** 超收转预收/退款未实现。
14. **REC-V14（缺失）** 核销撤销/反核销未实现。
15. **REC-V15（缺失）** write-off 要审批和原因未实现。
16. **REC-V16（缺失）** Statement 与 AR360 余额一致性未实现。
17. **REC-V17（缺失）** reconcile job 的幂等、重试和审计未实现。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `receipts` | 客户现金收款事件 |
| `receipts.so_id` | 收款对应 SO |
| `receipts.customer_id` | 收款客户 |
| `receipts.amount` | 单笔收款金额 |
| `receipt_items` | 无 DDL/写入的只读 scaffold |
| `sales_orders.received_amount` | SO 已收镜像 |
| `sales_orders.balance_amount` | SO 剩余镜像 |
| `payment_status` | SO 付款进度 |
| `ar_records` | DO 权责应收台账 |
| `ar_records.source_no` | 来源 DO 号 |
| `ar_records.balance` | 未被收款更新的台账余额 |
| `ar_records.status` | 初始 Unpaid，关闭写入口缺失 |
| `receivables` | 遗留并行结构，活动写入未证实 |
| `collections` | 遗留分配意图结构，活动写入未证实 |
| `collection_tasks` | 催收任务，不是 allocation |
| `treasury_payment_records` | AP 供应商付款 |
| Operational AR | SO−receipts |
| Statement AR | ar_records.balance |
| Allocation | 缺失实体/记录 |
| Reconciliation History | 缺失审计实体 |
| Write-off | 缺失核销动作 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Paid / Partial | SO payment_status |
| Unpaid | ar_records 初始状态 |
| Closed | AR 展示词汇，写路径缺失 |
| Allocated / Unallocated | 未实现 |
| Reconciled | 未实现 |
| Written Off | 未实现 |
| Reversed | 未实现 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| REC-E01 | create_receipt 只写 receipts/SO | 强 | `apps/finance/services.py` |
| REC-E02 | receipts INSERT 和 SO mirror UPDATE | 强 | `apps/finance/repository.py` |
| REC-E03 | DO→ar_records 单向 INSERT | 强 | `apps/inventory/services.py`、`apps/finance/services.py` |
| REC-E04 | receipts DDL 无 ar_id | 强 | `runtime/v14/legacy_support.py` |
| REC-E05 | ar_records/receivables/collections 并行 DDL | 强/结构 | `runtime/v14/legacy_support.py` |
| REC-E06 | receipt_items 仅只读 JOIN | 强（负证据） | `v15/business_lifecycle/context360.py` |
| REC-E07 | Statement 只用 ar_records | 强 | `document/nde_engine.py` |
| REC-E08 | receipts UI 明示从 SO 过账 | 强 | `templates/receipts.html` |
| REC-E09 | Receivable Center 显示静态 AR balance | 强 | `templates/receivable_center.html` |
| REC-E10 | A-011/A-014 分别记录 AR 与 Receipt 诚实边界 | 强 | `docs/reports/Business_Strong_A011_AR_Ops_Report.md`、`Business_Strong_A014_Receipt_Ops_Report.md` |
| REC-E11 | finance 模块规格表名与运行时分裂 | 中 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **receipt_items 是否曾在旧迁移创建 UNKNOWN。** 已查路径：legacy_support、database、backups、context360。
2. **隐藏自动核销 runtime 是否存在 UNKNOWN。** 已查路径：automation、scheduler、scripts、blueprint extracts。
3. **ar_records.ar_no 是否有批量生成 UNKNOWN。** 已查路径：Post service、DDL、jobs。
4. **Statement 是否应显示 receipts/未分配款 UNKNOWN。** 已查路径：NDE engine、statement template、reports。
5. **AR detail 是否计划展示 allocation UNKNOWN。** 已查路径：Finance routes/templates、receivable center links。
6. **Approval 是否预留 write-off/reconcile gate UNKNOWN。** 已查路径：apps/approval、workflow、business_modules。
7. **Commission 是否跨读 payment_status 与 AR UNKNOWN。** 已查路径：commission、sales、finance。
8. **core finance capability 是否有未挂载 allocation API UNKNOWN。** 已查路径：core/capabilities、registries、routes。
9. **invoices/payments 规格表是否在特定部署启用 UNKNOWN。** 已查路径：business_modules、runtime schema、repositories。
10. **GET 收款并发是否造成重复 receipt UNKNOWN。** 已查路径：create_receipt、DDL、事务与锁。
11. **坏账政策、容差和差额处理 UNKNOWN。** 已查路径：finance docs、write-off关键词、approval。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\context360.py`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
