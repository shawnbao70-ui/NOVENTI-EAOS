# 跨币种清账 / 汇兑损益

## Scope 与结论

本页叠加深挖 [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) 与 [`../ap-settlement-deepen/partial_clearing_writeoff.md`](../ap-settlement-deepen/partial_clearing_writeoff.md)：在**同币种清账已缺失**的前提下，跨币种清账与汇兑损益（realized FX）更加不存在。可确认的资金动作是：供应商付款扣银行余额、银行间同额转账、销售收款写 receipts 并推进 SO 已收字段。这些动作**不**选择 AR/AP 清算对象，**不**比较单据币与账户币，**不**计算汇差，**不**过账汇兑损益。

## 业务规则（稳定 ID）

1. **CCC-R01** 供应商付款绑定 supplier + bank account + amount，不绑定 AP/Invoice，故无法定义跨币核销对象。
2. **CCC-R02** 付款成功后不更新 `ap_records` / `purchase_invoices` 的 paid/balance/status。
3. **CCC-R03** 付款记录无 `currency`/`exchange_rate`/`fx_gain_loss` 字段。
4. **CCC-R04** 银行转账以单一金额同额加减，不产生 FX 明细行。
5. **CCC-R05** 转账不校验 from/to 账户币种是否相同。
6. **CCC-R06** 销售收款活动路径将 `receipts.currency` 写为 `"USD"`，即使报价可能为其他币种。
7. **CCC-R07** 收款推进 SO `received_amount`/`payment_status`，不写 AR 核销明细，更无汇差。
8. **CCC-R08** `ar_records` / `ap_records` 无币种维度，无法表达“原币余额 vs 本位币余额”。
9. **CCC-R09** 未见 allocation 表携带交易汇率、清算汇率与汇差金额。
10. **CCC-R10** 未见 realized FX gain/loss 凭证或费用/收益记录类型。
11. **CCC-R11** 未见尾差 write-off 区分“舍入”与“汇兑”。
12. **CCC-R12** AP Dashboard / 收款 KPI 直接汇总金额字段，不按币种分组或折算。
13. **CCC-R13** 资金总览跨账户合计在多币种并存时不具备可比性。
14. **CCC-R14** finance 知识包已将“多币种清算、汇率和汇兑差额”标为 UNKNOWN；本页升级为**强缺口（活动实现不存在）**。
15. **CCC-R15** 部分清账/write-off 实体缺失，使跨币清账无前置同币闭环可扩展。
16. **CCC-R16** NDE credit-note 等文档模板不是会计贷项，不能充当汇差调整凭证。
17. **CCC-R17** 价格试算 USD 换算结果不落库，不能作为清账汇率依据。
18. **CCC-R18** 因此 EAOS 不得将 Legacy 收付款登记解释为已完成的多币种清算能力。

## 校验（强 / 弱 / 缺失）

1. **CCC-V01（强）** 付款要求 Treasury.add 权限（资金动作门禁，非清账校验）。
2. **CCC-V02（强）** Invoice/AP 创建时 paid=0、balance=全额（同币初始化；无跨币语义）。
3. **CCC-V03（缺失）** 清账前单据币种 = 账户币种，或显式 FX 路径。
4. **CCC-V04（缺失）** 清算汇率来源（单据快照 / 付款日字典 / 人工审批）必填。
5. **CCC-V05（缺失）** `payment_amount_account_ccy` 与 `cleared_amount_doc_ccy` 勾稽。
6. **CCC-V06（缺失）** 汇差 = 按清算汇率折算差额，并过账损益。
7. **CCC-V07（缺失）** 部分清账后原币余额与本位币余额同时更新。
8. **CCC-V08（缺失）** 禁止用不同币种账户无汇差地核销外币 AP/AR。
9. **CCC-V09（缺失）** 转账跨币必须双币金额 + 汇率 + 汇差。
10. **CCC-V10（缺失）** 收款币种不得静默覆盖为 USD。
11. **CCC-V11（缺失）** GL 借贷平衡含汇兑损益科目。
12. **CCC-V12（弱）** UI 可显示账户币种 KPI 卡，不构成清账控制。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `treasury_payment_records.amount` | 未分配资金流出；无币种/汇差 |
| `treasury_bank_accounts.currency` | 账户名义币；付款不快照到付款行 |
| `treasury_transfer_records.amount` | 同额调拨；非 FX 兑换单 |
| `ap_records.amount/paid/balance` | 应付台账；付款不更新；无币种 |
| `purchase_invoices.*` | 发票镜像字段；无跨币清算 |
| `receipts.amount` / `currency` | 收款事实；活动路径币种常为 USD |
| SO `received_amount` / `balance_amount` | 订单收款进度，非 AR 核销、非汇差 |
| `ar_records.amount/balance` | 应收台账金额，无币种/汇差 |
| allocation / clearing history | **未建模** |
| realized FX gain/loss | **未建模** |
| fx rate on clearing | **未建模** |
| write-off（汇兑/尾差） | **未建模** |
| journal for FX | **未观察到** |
| 跨币 KPI 合计 | 直接相加，语义不安全 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| CCC-E01 | 付款 INSERT 列无币种/AP 锚点 | 强 | `apps/finance/treasury_pages.py`、`services.py` |
| CCC-E02 | 付款后无 AP/Invoice 更新 | 强 | 同上；邻包 ap-settlement-deepen |
| CCC-E03 | 转账同额无 FX 字段 | 强 | `apps/finance/services.py` |
| CCC-E04 | 收款硬编码 USD | 强 | `apps/finance/receipt_ar_expense_pages.py` |
| CCC-E05 | AP/AR DDL 无币种 | 强 | `runtime/v14/legacy_support.py` |
| CCC-E06 | payment/transfer DDL 无汇率 | 强 | 同上 treasury_* 段 |
| CCC-E07 | AP clearing 报告缺口 | 强 | `docs/reports/` 与 [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md) |
| CCC-E08 | 部分清账/write-off 缺失 | 强 | [`../ap-settlement-deepen/partial_clearing_writeoff.md`](../ap-settlement-deepen/partial_clearing_writeoff.md) |
| CCC-E09 | 账户余额直接合计 | 强 | `apps/finance/treasury_pages.py` |
| CCC-E10 | 全库无 exchange gain/fx difference 实现 | 强缺口 | 定向检索 apps/finance、templates、docs |

## UNKNOWN + 已查路径

1. **业务是否线下用同一银行账户只收付单一币种以规避问题 UNKNOWN。** 已查：账户创建表单、支付模板；无强制单币种策略代码。
2. **汇差是否记入费用模块手工单据 UNKNOWN。** 已查：expense 路径、tax_records、finance services 关键字。
3. **外部银行回单币种与系统不一致时如何处理 UNKNOWN。** 已查：reference_no/attachment 字段、对账模块检索。
4. **多币种客户是否被流程禁止 UNKNOWN。** 已查：credit control、convert gates、报价币种校验。
5. **历史付款备注是否曾手写汇差说明 UNKNOWN。** 已查：remark 字段语义；无结构化汇差。
6. **AR 双轨口径下是否有隐藏币种约定 UNKNOWN。** 已查：[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)、receipt-ar-reconcile-deepen。
7. **采购发票金额币种是否默认等于 PO 头币种（字段未传播）UNKNOWN。** 已查：invoice 创建服务、purchases 升级列消费点。

## 只读来源路径

`apps/finance/`（services、treasury_pages、receipt_ar_expense_pages、repository） · `runtime/v14/legacy_support.py` · `templates/payment_records.html` · `templates/ap_dashboard.html` · `templates/bank_accounts.html` · `business_modules/finance.md` · `docs/reports/` · 邻包 finance / ap-settlement-deepen / locale-commerce（只读）
