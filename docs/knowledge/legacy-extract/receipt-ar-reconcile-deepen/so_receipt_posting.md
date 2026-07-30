# SO 收款写入与付款镜像

## Scope与证据强度

本页深化 SO 快捷收款写入、`receipts` 事实表和 SO 镜像字段。收款主路径和实时 SUM 为强证据；币种、并发、撤销和 AR 勾兑为缺失。通用收款规则交叉引用 [`../finance/receipts_ar.md`](../finance/receipts_ar.md)，SO 展示交叉引用 [`../order-chain/so_payment_view.md`](../order-chain/so_payment_view.md)。

## 业务规则（稳定ID）

1. **SRP-R01** 活动客户收款事实表是 receipts，一笔一行。
2. **SRP-R02** 每笔 receipt 通过 so_id 关联整张销售订单，不关联 AR 行。
3. **SRP-R03** 快捷入口是有副作用 GET `/create_receipt/{so_id}`。
4. **SRP-R04** 创建要求 Receipts.add。
5. **SRP-R05** 服务先按 so_id 实时 SUM receipts.amount，不信任 SO 镜像。
6. **SRP-R06** 本次收款额固定为 `SO.total_amount - 已收 SUM`，没有金额输入表单。
7. **SRP-R07** 余额小于等于 0 时不插 receipt，只修正 SO 为 Paid。
8. **SRP-R08** receipt_no 由 SO id 与已收金额整数化结果拼接，不是独立序列。
9. **SRP-R09** payment_method 固定 Bank Transfer。
10. **SRP-R10** currency 固定 USD，不继承 Quote/SO 币种。
11. **SRP-R11** receipt 写入后先独立 commit。
12. **SRP-R12** 服务重新 SUM receipts，再写 SO 镜像并第二次 commit。
13. **SRP-R13** SO 镜像字段是 received_amount、balance_amount、payment_status。
14. **SRP-R14** Legacy SO 没有该路径使用的 paid_amount/remaining_amount 字段。
15. **SRP-R15** balance_amount 负值截为 0；不生成预收或贷项。
16. **SRP-R16** balance=0 时 payment_status=Paid，否则 Partial。
17. **SRP-R17** SO 详情实时 SUM receipts；SO 列表可读持久镜像，存在漂移可能。
18. **SRP-R18** 收款不改变 SO 履约 status。
19. **SRP-R19** 收款不读写 ar_records。
20. **SRP-R20** 未见 receipt_items 活动写入；它不是收款明细分配。
21. **SRP-R21** treasury_payment_records 是供应商/AP 出款，不是客户收款。
22. **SRP-R22** 客户删除可级联删除 receipts，没有 void/reversal 审计。

## 流程

1. 用户从 SO 页面点击 Create Receipt。
2. 路由检查 Receipts.add。
3. 服务读取 SO；不存在则返回销售订单列表。
4. 按 so_id 汇总既有 receipts。
5. 若已收不小于订单额，只回写 SO Paid。
6. 否则以全部剩余余额插入一笔 USD/Bank Transfer receipt 并提交。
7. 再次汇总 receipts。
8. 更新 SO received_amount、非负 balance_amount、Paid/Partial 并再次提交。
9. 重定向 receipts 列表；ar_records 不参与。

## 校验（强/弱/缺失）

1. **SRP-V01（强）** SO 必须存在。
2. **SRP-V02（强/权限）** 创建要求 Receipts.add。
3. **SRP-V03（强）** 剩余余额必须大于 0 才插 receipt。
4. **SRP-V04（强/读取）** receipts 列表/详情要求 Receipts.view。
5. **SRP-V05（弱/clamp）** 负余额镜像截为 0。
6. **SRP-V06（缺失）** 用户不能确认或输入部分收款金额。
7. **SRP-V07（缺失）** 未校验 SO 状态是否允许收款。
8. **SRP-V08（缺失）** 未校验 receipt 币种与 SO 币种一致。
9. **SRP-V09（缺失）** reference、附件、银行流水非必填。
10. **SRP-V10（缺失）** receipt_no 无可靠唯一生成/冲突重试。
11. **SRP-V11（缺失）** GET 无 idempotency key 或并发锁。
12. **SRP-V12（缺失）** receipt INSERT 与 SO 镜像更新不是单事务。
13. **SRP-V13（缺失）** 收款后不验证 ar_records 一致性。
14. **SRP-V14（缺失）** 未见正式 receipt void/refund/reversal。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `receipts.id` | 收款主键 |
| `receipt_no` | 由 SO/已收金额拼接的展示编号 |
| `so_id` | 收款对应整张 SO |
| `customer_id` | 从 SO 复制的客户 |
| `amount` | 本笔收款；快捷路径为剩余全额 |
| `payment_method` | 固定 Bank Transfer |
| `currency` | 固定 USD |
| `reference_no` | 可空参考号 |
| `attachment` | 可空附件 |
| `create_time` | 收款创建时间 |
| `sales_orders.total_amount` | 收款计算基数 |
| `received_amount` | receipts SUM 的持久镜像 |
| `balance_amount` | 非负剩余镜像 |
| `payment_status` | Unpaid/Uncollected、Partial、Paid |
| SO detail `received_amount` | 运行时实时 SUM |
| SO detail `balance` | max(total−SUM(receipts),0) |
| `ar_records.balance` | DO 应收余额；本路径不更新 |
| `receipt_items` | 只读 scaffold，不是活动分配表 |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Unpaid / Uncollected | SO 初始付款词汇不一致 |
| Partial | 已收小于订单额 |
| Paid | receipts SUM 达订单额 |
| Closed | ar_records 展示词汇，不由收款写入 |
| Overpaid | 未建模；负余额被截零 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| SRP-E01 | create_receipt 的 SUM、全额插入与双 commit | 强 | `apps/finance/services.py` |
| SRP-E02 | receipts INSERT 和 SO 镜像 UPDATE | 强 | `apps/finance/repository.py` |
| SRP-E03 | GET 路由与 Receipts 权限 | 强 | `apps/finance/router.py` |
| SRP-E04 | SO 详情实时 SUM 和余额截零 | 强 | `apps/sales/services.py` |
| SRP-E05 | SO 列表读取持久镜像 | 强 | `apps/sales/repository.py`、`templates/sales_orders.html` |
| SRP-E06 | 收款表和 SO 镜像 DDL | 强 | `runtime/v14/legacy_support.py` |
| SRP-E07 | Receipt UI 说明只能从 SO 过账 | 强 | `templates/receipts.html`、`sales_order_detail.html` |
| SRP-E08 | 客户余额按 SO−receipts | 强 | `apps/customer/services.py`、`repository.py` |
| SRP-E09 | A-014 验证收款 UI 诚实性 | 强 | `docs/reports/Business_Strong_A014_Receipt_Ops_Report.md` |
| SRP-E10 | finance 规格表名与运行时 receipts 分裂 | 中 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **部分收款 POST/API 是否在部署外存在 UNKNOWN。** 已查路径：apps/finance、apps/sales、templates、routes。
2. **receipt_items 是否曾有 DDL/迁移 UNKNOWN。** 已查路径：legacy_support、database、context360。
3. **SO 镜像漂移是否有后台重算 job UNKNOWN。** 已查路径：scheduler、scripts、reports、finance services。
4. **receipt_no 冲突的生产处理 UNKNOWN。** 已查路径：DDL、insert、异常处理。
5. **正式 void/refund/reversal 流程 UNKNOWN。** 已查路径：finance routes/services、templates、audit。
6. **取消 SO 是否允许收款 UNKNOWN。** 已查路径：sales status、finance create_receipt。
7. **真实 SO 币种如何传到 receipt UNKNOWN。** 已查路径：Quote/SO schema、Finance receipt。
8. **双 commit 中间失败的补偿 UNKNOWN。** 已查路径：repository commit、异常中间件、jobs。
9. **超收应记预收还是退款 UNKNOWN。** 已查路径：receipts、treasury、credit note/returns。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\customer\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
