# Return & Reversal Policy Deepen — Index

## Module Index

| Module | Evidence strength | Primary question | Primary locus |
|--------|-------------------|------------------|---------------|
| [`reopen_vs_return.md`](reopen_vs_return.md) | Strong / strong negative | Reopen 是否等于 Return/RMA？ | Inventory Reopen, Service scaffold |
| [`inventory_reverse_paths.md`](inventory_reverse_paths.md) | Strong / strong negative | 能否对称撤销 DO Ship？ | Inventory service/repository/ledger |
| [`ar_credit_cancel.md`](ar_credit_cancel.md) | Strong / strong negative | AR/Receipt 是否有 Credit/Cancel/Refund？ | Finance + DO invoice Type A |
| [`end_to_end_reversal_matrix.md`](end_to_end_reversal_matrix.md) | Strong cross-domain synthesis | 哪些事实可强/弱/不可回退？ | Sales/Inventory/Finance/TC/lifecycle |

## Cross-pack Map

| This pack | Read-only cross-reference | Boundary |
|-----------|---------------------------|----------|
| Reopen vs Return | `../fulfillment-deepen/returns_reversal.md` | fulfillment 基线；本包聚焦授权区别 |
| RMA | `../quality-compliance/claim_rma.md` | 客诉/RMA 缺口，不重写品质正文 |
| Ship reversal | `../ship-complete-deepen/`、fulfillment | 正向 Ship 权威不修改 |
| AR/Receipt | `../finance/receipts_ar.md`, `ar_receipt_reconciliation.md` | Finance 双轨事实只读引用 |
| commission | `../commission-ledger-deepen/tc_ledger_states.md` | Pending 无冲销路径 |

## Coverage Check

| Module | Rules | Validations | Data semantics | Evidence rows | UNKNOWN + searched paths |
|--------|------:|------------:|---------------:|--------------:|-------------------------:|
| reopen_vs_return | 21 | 13 | 17 | 17 | 9 |
| inventory_reverse_paths | 26 | 14 | 18 | 16 | 9 |
| ar_credit_cancel | 26 | 14 | 20 | 17 | 9 |
| end_to_end_reversal_matrix | 22 | 14 | 20 | 23 | 10 |

## Reversal Strength Summary

| Domain | Strong | Weak | Missing |
|--------|--------|------|---------|
| SO/DO status | Complete→Reopen→Open | status-only manual changes | coordinated cancel |
| Inventory | positive Ship/Adjust | manual +qty adjustment | linked unship/return receipt |
| Inventory ledger | append positive actions | free-text compensation | reversal link/idempotency |
| Receipt | positive receipt create | none | void/refund |
| SO payment mirror | positive recompute | manual/data repair UNKNOWN | reversal-triggered recompute |
| `ar_records` | positive Post AR | duplicate warning | credit/cancel/reverse |
| Credit Note | document registry/template | printable artifact | accounting posting |
| TC commission | Pending creation | none | void/reverse/payment |
| RMA | vocabulary/scaffold | none | authorization-to-close lifecycle |

## Critical Policy Conclusions

1. Reopen 是状态动作，不能授权退货。
2. Inventory Adjust 是局部补偿，不能证明 Ship 被撤销。
3. Credit Note 文档与 AR 红冲是不同事实；Legacy 只证实前者表面。
4. 没有端到端事务、saga 或 reconciliation 将库存、现金、AR 与佣金一起回退。
5. 任何迁移都必须保留原正向 posting，并以链接的反向事件表达冲销，不能直接覆盖历史。

## Package Boundary

本包仅新增本目录六份知识文档。未修改 fulfillment、quality-compliance、finance、commission、ship-complete 或其他邻包正文。
