# Credit Note 是否入账 / 冲 AR

## Scope 与结论

交叉引用权威（不重写）：[`../tax-invoice-deepen/invoice_void_credit.md`](../tax-invoice-deepen/invoice_void_credit.md)、[`../return-reversal-policy-deepen/ar_credit_cancel.md`](../return-reversal-policy-deepen/ar_credit_cancel.md)、[`../tax-invoice-deepen/nde_vs_ar_invoice.md`](../tax-invoice-deepen/nde_vs_ar_invoice.md)。本页专攻「Credit Note 会计后果」：是否入账、是否冲减 `ar_records`、是否产生税票红冲。

**结论：** Credit Note / Debit Note **仅有模板映射与极简 HTML 壳**；**不**入账、**不**冲 AR、**不**写税票红冲。活动正向路径只有 Post AR INSERT；未见负向 AR、未见 `UPDATE/DELETE ar_records`、未见 credit memo application、未见 return/reopen 联动冲应收。打印 Credit Note ≠ 贷项已过账。

## 业务规则（稳定 ID）

1. **CNA-R01** `document/nde_engine.py` 将 `"Credit Note"` / `"Debit Note"` 映射到 `documents/credit_note.html` / `debit_note.html`。  
2. **CNA-R02** `_DOC_FAMILY` / `_LAYOUT_PROFILE` **未**注册 Credit/Debit Note；解析落到默认 quotation family —— 模板挂名而非完整文档族。  
3. **CNA-R03** `credit_note.html` 仅 include product_table + financial summary；无贷项专用会计块。  
4. **CNA-R04** 未见 `build_nde_credit_*` 或 print_preview 模块别名把业务贷项表接到 Credit Note。  
5. **CNA-R05** Post AR 成功路径只 INSERT 正数 `ar_records`；无配对 Credit/Void 命令。  
6. **CNA-R06** 同 DO 重复 Approve 可再插 AR；用 warning 而非冲销旧行后重开。  
7. **CNA-R07** apps/finance 与 apps/inventory 活动代码未见 `DELETE FROM ar_records` / `UPDATE ar_records SET status=…` 取消/贷项 writer（与 return-reversal 一致）。  
8. **CNA-R08** Receipt 不更新 `ar_records.balance/status`；因此也不存在「收款后开贷项勾兑」闭环。  
9. **CNA-R09** DO Reopen / SO cancel 不自动撤销 AR（邻包已证）。  
10. **CNA-R10** 无红字发票号、原票引用、贷项金额分配、税控红冲回执字段模型。  
11. **CNA-R11** 无 Type A「Issue Credit / Void AR」对称人工确认面（相对 Post AR 存在）。  
12. **CNA-R12** 销售税票主账缺失时，「税票贷项/红冲」无承载实体。  
13. **CNA-R13** `DEBIT_NOTE` 同为文档 registry/模板层；与 AR row 无连接。  
14. **CNA-R14** 设计指南可有 void 水印 class —— 视觉规范，不是会计冲销工作流。  
15. **CNA-R15** EAOS 不得把 Credit Note 模板文件存在解释为已实现贷项模块或已冲 AR。  
16. **CNA-R16** 本页相对邻包的深化点：把「模板有 / 入账无 / 冲 AR 无 / 报税红冲无」收束为报税交界结论，服务 tax-filing 边界。  

## 入账后果矩阵

| 动作 / 期望后果 | 观察到 | 强度 |
|---|---|---|
| 打印 Credit Note HTML | 模板可存在 | 元数据/模板 |
| INSERT 负向 `ar_records` | 无 | 缺失 |
| 降低原 AR `balance` | 无 | 缺失 |
| 原 AR status→Credited/Void | 无活动 writer | 缺失 |
| 创建税票红冲实体 | 无销售税票主账 | 缺失 |
| 写入 `tax_records` 负项 | 无（仅测试正项 VAT） | 缺失 |
| 与 Receipt 勾兑后退款 | 无 receipt void/refund | 缺失 |
| 与 Return/Reopen 联动 | 无自动冲 AR | 缺失 |
| 重复 Post AR | 可叠加 | 风险（非贷项） |

## 流程（缺失汇合）

1. 用户可 Post AR 建立 Unpaid 应收。  
2. 若需贷项更正：活动系统不提供「选原 AR → 授权 → 贷项入账 → 冲余额 → 可选打印 Credit Note → 税申报调整」。  
3. 打印层即便渲染 Credit Note 壳，也不会自动生成负向应收或税票冲销。  
4. 不安全替代（未产品化）：再次 Post AR（重复）、或库外改数 —— 都不是受控贷项会计。  

## 校验（强 / 弱 / 缺失）

1. **CNA-V01（强/缺席）** 贷项必须有授权命令与审计 —— **缺失**。  
2. **CNA-V02（强/缺席）** 贷项必须引用原 `ar_records.id` / 原发票号 —— **缺失**。  
3. **CNA-V03（强/缺席）** 贷项金额不得超过原开放余额 —— **缺失**。  
4. **CNA-V04（强）** Post AR 需要 human_confirm；对称 Credit 面不存在。  
5. **CNA-V05（缺失）** Credit Note 打印前必须已入账贷项事实 —— 模板可独立存在。  
6. **CNA-V06（缺失）** 贷项必须同步税基/税额红冲 —— 无算税与税票实体。  
7. **CNA-V07（缺失）** 已收款部分禁止直接 void，须走退款路径 —— 因无勾兑，规则无从附着。  
8. **CNA-V08（弱）** 重复 AR warning 存在，但不能替代冲销校验。  
9. **CNA-V09（缺失）** Credit/Debit 必须进入 `_DOC_FAMILY` 才算完整文档能力 —— 当前未注册。  
10. **CNA-V10（强缺席）** apps 层无 ar_records 状态推进器可被 credit 复用。  
11. **CNA-V11（缺失）** 贷项过账权限与 Type A 对等。  
12. **CNA-V12（缺失）** 贷项后 Customer AR 与 Receivable Center 双口径一致回写。  

## 数据含义

| 数据 / 名称 | Legacy 含义 |
|---|---|
| Credit Note 模板 | 打印壳，非贷项主账 |
| Debit Note 模板 | 继承 Credit Note 壳 |
| NDE 模板映射键 | 文档类型名 → HTML 路径 |
| `_DOC_FAMILY` 缺席 | Credit 非完整文档族 |
| `ar_records.status='Unpaid'` | 新计提默认态；未见 Credited/Void 写入 |
| 负向 `ar_records.amount` | 未见生成策略 |
| 原票号 / 红字信息表 | 未建模 |
| credit/reversal source ID | 未建模 |
| write-off / bad debt | 清算 deepen 已证缺失；此处不重复实现 |
| Type A Post AR | 唯一对称的人工财务确认面（正向） |
| Receipt | SO 现金事件；不冲 AR |
| DO Reopen | 物流状态动作，不冲 AR |
| `tax_records` 测试 VAT 行 | 非贷项税冲销 |
| 销售税票红冲 | 无实体可挂 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| CNA-E01 | Credit/Debit 模板映射 | 强 | `document/nde_engine.py`（NDE_TEMPLATE_MAP） |
| CNA-E02 | `_DOC_FAMILY` 无 Credit/Debit | 强 | `document/nde_engine.py` |
| CNA-E03 | Credit Note 模板体极简 | 强 | `templates/documents/credit_note.html` |
| CNA-E04 | `_legacy_create_ar` 仅正向 INSERT | 强 | `apps/finance/services.py` |
| CNA-E05 | apply_do_invoice 无 credit/void 分支 | 强 | `apps/inventory/services.py` |
| CNA-E06 | finance/inventory 无 ar_records UPDATE/DELETE 活动路径 | 强缺席 | 邻包检索结论 + 本包复核 services |
| CNA-E07 | return-reversal：CREDIT_NOTE 仅文档表面 | 强 | [`../return-reversal-policy-deepen/ar_credit_cancel.md`](../return-reversal-policy-deepen/ar_credit_cancel.md) |
| CNA-E08 | tax-invoice void/credit 缺席矩阵 | 强 | [`../tax-invoice-deepen/invoice_void_credit.md`](../tax-invoice-deepen/invoice_void_credit.md) |
| CNA-E09 | DOCUMENT_ENGINE 列出 Credit Note 类型（意图） | 中 | `docs/reports/DOCUMENT_ENGINE_ARCHITECTURE.md`（邻包已引） |
| CNA-E10 | 重复 AR warning ≠ 贷项 | 强 | `apps/inventory/services.py`（`build_do_invoice_context`） |

## UNKNOWN + 已查路径

1. **DBA 是否用手工 SQL 插入负 AR 或改 balance UNKNOWN。** 已查：活动 Python 写路径；未读生产库。  
2. **是否存在未合并分支实现 credit memo API UNKNOWN。** 已查：`apps/finance`、`apps/inventory`、`document/nde_engine.py`、void/credit_note/红冲关键词。  
3. **Credit Note 是否曾通过通用 print_preview 手工 module 名渲染 UNKNOWN。** 已查：nde_engine module 分支（invoice/ar/delivery/quote/proforma 等）；未见 credit 别名。  
4. **采购退货是否在库存侧产生应付贷项 UNKNOWN。** 已查：finance AP/invoice 路径；详见 procurement/return 邻包，本页不断言实现。  
5. **未来税控红字信息表是否规划 UNKNOWN。** 已查：business_modules/finance Future Scope、tax capability README；无红冲设计落地。  
6. **智能状态别名 void→cancelled 是否作用于发票 UNKNOWN。** 已查：邻包 `config/smart_business_s07.py` 叙述；未证发票状态机消费。  
7. **运营是否用「再开一张更小 AR」模拟贷项 UNKNOWN。** 已查：重复 Post AR 仅 warning；无产品化贷项向导。  

## 只读来源路径

`document/nde_engine.py` · `templates/documents/credit_note.html` · `templates/documents/debit_note.html` · `apps/finance/services.py` · `apps/inventory/services.py` · `docs/knowledge/legacy-extract/tax-invoice-deepen/invoice_void_credit.md` · `docs/knowledge/legacy-extract/return-reversal-policy-deepen/ar_credit_cancel.md` · `docs/reports/DOCUMENT_ENGINE_ARCHITECTURE.md` · `business_modules/finance.md`
