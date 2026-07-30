# 收款、应收与勾兑深化索引

## 文档导航

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`so_receipt_posting.md`](so_receipt_posting.md) | SO 收款写入、镜像字段和事务 | `SRP-*` |
| [`ar_records_lifecycle.md`](ar_records_lifecycle.md) | DO Post AR、状态/余额和重复风险 | `ARL-*` |
| [`dual_balance_views.md`](dual_balance_views.md) | 经营余额与台账余额双视图 | `DBV-*` |
| [`reconcile_absence.md`](reconcile_absence.md) | 勾兑、核销、分配与作业缺失 | `REC-*` |

## 邻包交叉引用

| 权威主题 | 文档 |
|---|---|
| 收款与 AR 总览 | [`../finance/receipts_ar.md`](../finance/receipts_ar.md) |
| AR/Receipt 对账缺口 | [`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) |
| SO 收款双视图 | [`../order-chain/so_payment_view.md`](../order-chain/so_payment_view.md) |
| 客户余额口径 | [`../customer-deepen/ar_balance_view.md`](../customer-deepen/ar_balance_view.md) |

## 核心结论

1. 客户收款活动表是 `receipts`；快捷 GET 收取 SO 当时全部剩余余额。
2. 收款后独立提交 receipt，再写 SO 的 `received_amount/balance_amount/payment_status` 镜像。
3. SO 实际字段不是 `paid_amount/remaining_amount`；相应语义由 received/balance 表达。
4. DO Post AR 只 INSERT `ar_records`：Unpaid，amount=balance=DO 总额。
5. ar_records 创建后未找到 balance/status 更新入口；收款不勾兑它。
6. Customer360、`/ar`、AR Dashboard 使用 `SUM(SO)-SUM(receipts)`。
7. Statement 与 Receivable Center 使用 `ar_records.balance`。
8. `receipt_items` 只有只读 JOIN 痕迹，无 DDL/写入，不是 allocation 实现。
9. 全库未找到 payment allocation、核销、write-off、reconcile job 或一致性审计。

## 主要证据

- `apps/finance/`
- `apps/sales/`
- `apps/inventory/`
- `apps/customer/`
- `templates/`
- `document/nde_engine.py`
- `runtime/v14/legacy_support.py`
- `business_modules/`
- `docs/reports/Business_Strong_A011_AR_Ops_Report.md`
- `docs/reports/Business_Strong_A014_Receipt_Ops_Report.md`
- `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md`
