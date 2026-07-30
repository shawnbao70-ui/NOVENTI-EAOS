# Legacy Knowledge Extract — Commission Ledger Deepen Pack

**Source:** `H:\Workspace\EZAM_CRM - 9.0` (read-only)  
**Writable home:** `docs/knowledge/legacy-extract/commission-ledger-deepen/**`  
**Verified:** 2026-07-23

## Scope

本包深化 Quote→SO 转换佣金、业务员等级费率、TC ledger 状态和 Finance 结算边界。它记录实际计算与持久化事实，也明确 Commission Center 展示规则、calculator、periods、rebates 和 Treasury/AP/Payroll 之间未接通的边界。

## Modules

- [Commission on Convert](commission_on_convert.md) — 转 SO 时 TC ledger 写入与失败边界
- [Commission Rate Source](commission_rate_source.md) — salesperson level 执行费率及平行规则源
- [TC Ledger States](tc_ledger_states.md) — Pending 创建与缺失的审批/发放状态机
- [Commission–Finance Boundary](commission_finance_boundary.md) — Sales 计算真相与 Finance 未完成结算边界
- 汇总见 [INDEX.md](INDEX.md)

## Evidence posture

- canonical 佣金在 Sales 转单时以 SO 总额和 salesperson level rate 计算。
- `commission_rules` 可展示/新增，但不参与 canonical 计算；calculator、SO 预留列和 distributor level 又形成不参与主链的平行费率源。
- 费率缺失退化为零，钩子异常被静默吞没；SO 成功不证明 TC row 成功。
- TC ledger 只观察到 Pending 新建和只读列表；无 Approved/Paid/Rejected/Voided writer。
- commission periods 不关联 TC rows，也不执行关账。
- Finance registry 声明 TC/commission 边界，但 Finance service、Treasury/AP/Expense/Payroll 未接台账。

## Hard boundaries

- Pending TC 不是已批准应付、会计费用或已支付佣金。
- Commission Center 的 `commission_rules` 不是 canonical 执行规则。
- `salesperson_commissions` calculator/ranking 不是 TC ledger。
- 默认 A/B/C 的 30/25/20 是 Legacy seed，不是应采用的政策。
- Treasury supplier payment、AP 和 expense 记录不能推断为佣金付款。
- TC 没有可证现金兑换、币种、税或 payroll 语义。
- 本包不修改 `finance/settlement-rules.md`、sales-deepen、commercial-terms 或其他 pack。
