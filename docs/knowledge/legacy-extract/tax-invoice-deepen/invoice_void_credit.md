# 作废 / 红冲 / 贷项路径有无

## Scope 与结论

交叉引用：[`../finance/invoices.md`](../finance/invoices.md)、[`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md)、[`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md)、[`../ap-settlement-deepen/partial_clearing_writeoff.md`](../ap-settlement-deepen/partial_clearing_writeoff.md)。

**结论：** Legacy **没有**销售税务发票或 AR 的活动作废/红冲/贷项入账路径。可见残留是：NDE 模板名 `Credit Note` / `Debit Note`、设计文档中的 Void 水印 class、以及业务叙事里的「合理删除或作废」意图。`ar_records` / `purchase_invoices` 在活动服务中未见 DELETE、未见 status→Void/Cancelled/Credited、未见负向贷项行或红字发票实体。重复 Post AR 会叠加，而不是冲销重开。

## 业务规则（稳定 ID）

1. **IVC-R01** DO Post AR 成功路径只 INSERT `ar_records`，无配对 void/reversal 命令。
2. **IVC-R02** 同 DO 重复 Approve 可再次 INSERT；系统用 warning 而非冲销旧行。
3. **IVC-R03** apps/finance 与 apps/inventory 活动代码未见 `DELETE FROM ar_records` / `UPDATE ar_records SET status=...`。
4. **IVC-R04** 采购发票创建后未见 void/cancel/credit 路由；状态初始化 `Unpaid`，无作废态词汇落地。
5. **IVC-R05** `document/nde_engine.py` 将 `Credit Note`、`Debit Note` 映射到 HTML 模板。
6. **IVC-R06** `_DOC_FAMILY` / `_LAYOUT_PROFILE` **未**注册 Credit/Debit Note；解析将落到默认 quotation family，属模板挂名而非完整文档族。
7. **IVC-R07** `templates/documents/credit_note.html` 仅为 product_table + financial 片段；`debit_note.html` extends 它。
8. **IVC-R08** 未见 `build_nde_credit_*` 或 print_preview 模块别名把业务贷项表接到 Credit Note。
9. **IVC-R09** 设计指南列出 `nde-watermark-void` 等水印 class —— 视觉规范，不是作废工作流。
10. **IVC-R10** `config/smart_business_s07.py` 有 `"void": "cancelled"` 状态别名映射意图；不足以证明发票 void 命令存在。
11. **IVC-R11** 收款不更新 `ar_records.balance/status`；因此也不存在「收款后红冲应收」的闭环。
12. **IVC-R12** DO Reopen/Complete 不自动创建、撤销或重算 AR（ship-complete 已证）。
13. **IVC-R13** 无红字发票号、原票引用、贷项金额分配、税务红冲回执字段模型。
14. **IVC-R14** 无 AI/人类确认 Type A「Void AR / Issue Credit」表面（相对 Post AR 存在）。
15. **IVC-R15** 销售税票主账本身缺失时，「税票作废」无承载实体（见 tax_invoice_entity）。
16. **IVC-R16** EAOS 不得把 Credit Note 模板文件存在解释为已实现贷项模块。

## 路径有无矩阵

| 能力 | 有无 | 证据形态 |
|---|---|---|
| Post AR（正向计提） | 有 | Type A 路由 + INSERT |
| Void AR | 无 | 无 UPDATE/DELETE 活动路径 |
| Credit Note 入账 | 无 | 仅模板映射 |
| Debit Note 入账 | 无 | 模板 extends Credit Note |
| 红冲税票 | 无 | 无销售税票实体 |
| 采购发票作废 | 无 | 无 cancel 路由 |
| Void 水印样式 | 设计有 | DOCUMENT_STYLE_GUIDE |
| 重复计提 | 有（风险） | warning only |

## 流程（缺失汇合）

1. 用户可 Post AR 建立 Unpaid 应收。
2. 若需更正：活动系统不提供「作废旧 AR → 开贷项 → 重开」向导。
3. 可能的不安全替代（未产品化、未强制）：再次 Post AR（重复）、或库外手工改数 —— 二者都不是受控红冲。
4. 打印层即便渲染 Credit Note 壳，也不会自动生成负向 `ar_records` 或税票冲销。

## 校验（强 / 弱 / 缺失）

1. **IVC-V01（强/缺席）** 作废必须有授权命令与审计 —— **缺失**。
2. **IVC-V02（强/缺席）** 冲销必须引用原 `ar_records.id` / 原发票号 —— **缺失**。
3. **IVC-V03（强/缺席）** 贷项金额不得超过原开放余额 —— **缺失**。
4. **IVC-V04（强）** Post AR 需要 human_confirm；对称 void 面不存在。
5. **IVC-V05（缺失）** 已收款/部分收款禁止直接 void —— 因无收款勾兑，规则无从附着。
6. **IVC-V06（缺失）** Credit Note 打印前必须已入账贷项事实 —— 模板可独立存在。
7. **IVC-V07（缺失）** 红冲必须保持借贷合计为零并过账税申报 —— 无。
8. **IVC-V08（弱）** 重复 AR warning 存在，但不能替代冲销校验。
9. **IVC-V09（缺失）** Void 水印与业务状态机联动 —— 仅设计表。
10. **IVC-V10（缺失）** 采购发票作废后回滚 AP —— 无。
11. **IVC-V11（缺失）** Credit/Debit 必须进入 `_DOC_FAMILY` 才算完整文档能力 —— 当前未注册。
12. **IVC-V12（强缺席）** apps 层无 ar_records 状态推进器可被 void 复用。

## 数据含义

| 数据 / 名称 | Legacy 含义 |
|---|---|
| `ar_records.status='Unpaid'` | 新计提默认态；未见 Closed/Void 写入 |
| Credit Note 模板 | 打印壳，非贷项主账 |
| Debit Note 模板 | 继承 Credit Note 壳 |
| `nde-watermark-void` | CSS/设计 class 名 |
| `"void":"cancelled"` 映射 | 智能状态别名配置意图 |
| 原票号 / 红字信息表 | 未建模 |
| 负向 `ar_records.amount` | 未见生成策略 |
| `purchase_invoices.status` | Unpaid 初始化；非 Void 机 |
| `ap_records` | 随采购发票建立；未见因作废回滚 |
| DO Reopen | 物流状态动作，不冲 AR |
| 重复 `source_no` AR 行 | 多条并存风险，非贷项 |
| write-off | AP/AR 清算 deepen 已证缺失；此处不重复实现 |
| 税控红冲回执 | 无 |
| Type A Post AR | 唯一对称的人工财务确认面（正向） |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| IVC-E01 | `_legacy_create_ar` 仅 INSERT | 强 | `apps/finance/services.py` |
| IVC-E02 | apply_do_invoice 无 void 分支 | 强 | `apps/inventory/services.py` |
| IVC-E03 | finance/inventory 无 ar_records UPDATE/DELETE | 强缺席 | `apps/finance/**/*.py`、`apps/inventory/**/*.py` 检索 |
| IVC-E04 | Credit/Debit 模板映射 | 强 | `document/nde_engine.py` |
| IVC-E05 | Credit Note 模板体极简 | 强 | `templates/documents/credit_note.html`、`debit_note.html` |
| IVC-E06 | `_DOC_FAMILY` 无 Credit/Debit | 强 | `document/nde_engine.py` |
| IVC-E07 | Void 水印设计表 | 中 | `docs/design/DOCUMENT_STYLE_GUIDE.md`（及 docs/ui 副本） |
| IVC-E08 | void→cancelled 别名 | 弱 | `config/smart_business_s07.py` |
| IVC-E09 | AR 不因收款关闭 | 强 | [`../finance/ar_receipt_reconciliation.md`](../finance/ar_receipt_reconciliation.md) |
| IVC-E10 | Reopen 不冲 AR | 强 | [`../ship-complete-deepen/do_invoice_ar.md`](../ship-complete-deepen/do_invoice_ar.md) |
| IVC-E11 | DOCUMENT_ENGINE 列出 Credit Note 类型 | 中/意图 | `docs/reports/DOCUMENT_ENGINE_ARCHITECTURE.md` |
| IVC-E12 | 开发叙事「删除或作废」非实现 | 弱/意图 | `docs/development/BUSINESS_STRONG_AND_SMART_TERMINAL_PROGRAM.md` |

## UNKNOWN + 已查路径

1. **DBA 是否用手工 SQL 作废 AR UNKNOWN。** 已查：活动 Python 写路径、reports；未读生产库。
2. **是否存在未合并分支实现 credit memo API UNKNOWN。** 已查：`apps/finance`、`apps/inventory`、`document/nde_engine.py`、routes 关键词 void/credit_note/红冲/作废。
3. **Credit Note 是否曾通过通用 print_preview 手工 module 名渲染 UNKNOWN。** 已查：nde_engine module 分支（invoice/ar/delivery/quote/proforma 等）；未见 credit 别名。
4. **智能状态别名 void 是否作用于报价/订单而非发票 UNKNOWN。** 已查：`config/smart_business_s07.py` 映射行；未证发票状态机消费。
5. **采购退货是否在库存侧产生应付贷项 UNKNOWN。** 已查：finance AP/invoice 路径、本包 void 检索；详见 procurement/return 邻包，不在本页断言实现。
6. **未来税控接口是否计划用红字信息表 UNKNOWN。** 已查：business_modules/finance.md Future Scope、tax capability README；无红冲设计落地。
7. **watermark void 是否被任何运行模板 class 实际输出 UNKNOWN。** 已查：设计指南；nde_engine `watermark` extra 槽；未追踪到业务状态自动映射 void。

## 只读来源路径

`apps/finance/` · `apps/inventory/` · `document/nde_engine.py` · `templates/documents/credit_note.html` · `templates/documents/debit_note.html` · `docs/design/DOCUMENT_STYLE_GUIDE.md` · `docs/reports/DOCUMENT_ENGINE_ARCHITECTURE.md` · `config/smart_business_s07.py` · `docs/development/BUSINESS_STRONG_AND_SMART_TERMINAL_PROGRAM.md` · `docs/knowledge/legacy-extract/finance/` · `docs/knowledge/legacy-extract/ship-complete-deepen/` · `docs/knowledge/legacy-extract/ap-settlement-deepen/`
