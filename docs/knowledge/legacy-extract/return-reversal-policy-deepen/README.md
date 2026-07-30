# Return & Reversal Policy Deepen — Legacy Knowledge Pack

## Purpose

本包深化 EZAM_CRM 9.0 从 SO/DO/库存到 Receipt/AR/佣金的退货、重开、取消和冲销能力。它严格区分状态回开、人工数量调整、文档打印与真正的反向业务交易。

## Modules

- [`reopen_vs_return.md`](reopen_vs_return.md)：DO Reopen 与 RMA/退货授权的边界。
- [`inventory_reverse_paths.md`](inventory_reverse_paths.md)：Ship、库存双写、ledger 与人工 Adjust 的非对称性。
- [`ar_credit_cancel.md`](ar_credit_cancel.md)：Post AR、Receipt、Credit Note、红冲与退款缺口。
- [`end_to_end_reversal_matrix.md`](end_to_end_reversal_matrix.md)：SO/DO/库存/现金/AR/佣金/追踪的强弱缺失矩阵。
- [`INDEX.md`](INDEX.md)：证据强度、覆盖门槛和跨包索引。

## Evidence Posture

1. **Strong**：活动 Inventory/Finance/Sales service、repository、router 和模板。
2. **Strong negative**：在 schema、writers、routes、templates、reports 中未观察到 RMA、unship、refund、AR reversal 或 TC reversal。
3. **Metadata-only**：Credit Note、complaint、returns 等 registry/graph/template 词汇不等同运行交易。
4. **UNKNOWN**：私有部署 schema、线下处理和异常请求最终 rollback 无法由只读源码确认。

## Critical Honesty Findings

- DO Reopen 只把 DO/SO 改回 Open；库存、Ship ledger、AR、Receipt、TC 不变。
- 正数 Inventory Adjust 可人工补量，但不引用原 Ship/RMA，也不解除 Ship 防重。
- Post AR 对重复 source 只告警仍可提交；没有对称红冲/Credit Note posting。
- Receipt 先 commit，SO payment mirror 再 commit；没有 void/refund 触发反向汇总。
- TC 只有 Pending 正向写入；SO 取消、Reopen 或退货不冲销。

## Hard Boundaries

- 本包不提供 Return、Unship、Refund、Credit、AR reversal 或 commission reversal CRUD。
- 不修改 ship-complete、fulfillment、quality、finance、commission 等邻包权威正文。
- 不把状态 Open、打印 Credit Note 或 Manual Adjustment 解释为完整回退。
- 只写 `docs/knowledge/legacy-extract/return-reversal-policy-deepen/**`。

## Read-only Roots

- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\service\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\`
- `H:\Workspace\EZAM_CRM - 9.0\document\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
