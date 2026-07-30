# 收款、应收与勾兑深化包

## 目的

本包核验 Legacy 中 SO 收款、DO Post AR、客户余额与 Statement 台账之间的真实关系。重点记录三类并行事实：`receipts` 驱动 SO 收款镜像、`ar_records` 驱动 DO 应收台账、客户页面按 SO−Receipts 计算经营余额。

## 边界

- 收款与 AR 总览继续以 [`../finance/`](../finance/) 为权威。
- SO 付款展示继续以 [`../order-chain/so_payment_view.md`](../order-chain/so_payment_view.md) 为权威。
- 客户余额展示继续以 [`../customer-deepen/ar_balance_view.md`](../customer-deepen/ar_balance_view.md) 为权威。
- 本包只深化写入、生命周期、双视图和勾兑缺失，不修改邻包或提出业务模块实现。

## 内容

- [`so_receipt_posting.md`](so_receipt_posting.md)：SO 快捷收款、receipts 与 SO 镜像。
- [`ar_records_lifecycle.md`](ar_records_lifecycle.md)：DO Post AR、ar_records 初值和冻结状态。
- [`dual_balance_views.md`](dual_balance_views.md)：Customer360/AR360 与 Statement/Receivable Center 双口径。
- [`reconcile_absence.md`](reconcile_absence.md)：allocation、matching、write-off 与 reconcile 作业缺失。
- [`INDEX.md`](INDEX.md)：稳定 ID、证据和交叉引用索引。

## 证据口径

- **强**：活动路由、service/repository、DDL、模板和报告可互证。
- **弱**：UI warning、镜像字段、残留表或文档链路。
- **缺失**：无写路径、无状态更新、无分配实体、无对账作业。
- `SO Paid` 不等于 `ar_records Closed`；`Post AR` 不等于税票；Statement 总额不等于 Customer360 余额。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`
