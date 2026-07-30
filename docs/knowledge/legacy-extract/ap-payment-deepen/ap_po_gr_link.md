# AP、PO 与收货追溯

## Scope与证据强度

本页追踪 `purchases → inventory_ledger → purchase_invoices → ap_records`。结构化 PO/Invoice/AP 关联较强；收货只靠 ledger remark 软链接，`purchase_receipts` 是未使用 DDL，且无三单匹配。

## 业务规则（稳定ID）

1. **PGL-R01** 新 PO 默认 Draft 并绑定 supplier_id。
2. **PGL-R02** PO 行通过 purchase_id 关联头。
3. **PGL-R03** 行金额为 qty×cost_price。
4. **PGL-R04** PO Approve 要求 Draft、有行、human_confirm。
5. **PGL-R05** Draft/Open/Pending 均被归一为可收货 open。
6. **PGL-R06** Receive 一次按全部有效 PO 行收货，不支持部分数量。
7. **PGL-R07** Receive 同步更新 inventory、products stock 和 inventory_ledger。
8. **PGL-R08** ledger trans_type 固定 `PO Receipt`。
9. **PGL-R09** ledger remark=`PO-{purchase_id}` 是收货软追溯键。
10. **PGL-R10** PO status 与 ledger 双重防止重复收货。
11. **PGL-R11** 收货成功后 PO status=Received。
12. **PGL-R12** purchase_receipts 表存在但活动收货不写入。
13. **PGL-R13** 一 PO 一 invoice 由 purchase_id 查重。
14. **PGL-R14** 发票 supplier_id 和 amount 从 PO 头复制。
15. **PGL-R15** 发票创建同步生成 AP。
16. **PGL-R16** AP 经 invoice_id 间接追溯 PO，没有 purchase_id。
17. **PGL-R17** UI 仅 Received 后显示开票。
18. **PGL-R18** 服务端开票不验证 PO 状态或 ledger 收货。
19. **PGL-R19** 发票不引用 receipt_id/GR 行。
20. **PGL-R20** 发票金额不与收货量、PO 行重算金额做匹配。
21. **PGL-R21** 官方报告将三单匹配列为未完成。
22. **PGL-R22** create_purchase_invoice 路由缺 RBAC。

## 流程

1. Supplier 下建立 PO 头与行。
2. 可选 Approve 将 Draft 改 Open；Draft 也可直接 Receive。
3. Receive 全量入库并写 `PO Receipt` ledger。
4. PO 标记 Received。
5. UI 显示 Create Invoice，但直接 URL 可绕过 Received。
6. Invoice 通过 purchase_id 关联 PO。
7. AP 通过 invoice_id 关联 Invoice，再间接关联 PO。
8. 无结构化 GR 实体或三单匹配。

## 校验（强/弱/缺失）

1. **PGL-V01（强）** PO 必须有 supplier_id。
2. **PGL-V02（强）** 添加行要求 PO open。
3. **PGL-V03（强）** Approve 要求 Draft、有行和确认。
4. **PGL-V04（强）** Receive 要求 PO 存在且未 received。
5. **PGL-V05（强）** Receive 检查 ledger 幂等。
6. **PGL-V06（强）** Receive 要求至少一行和库存行。
7. **PGL-V07（弱）** qty≤0 行被静默跳过。
8. **PGL-V08（强/应用）** 同 PO 不可重复 invoice。
9. **PGL-V09（缺失）** Invoice 不要求 Received。
10. **PGL-V10（缺失）** Invoice 不验证 ledger/GR。
11. **PGL-V11（缺失）** 无 PO/GR/Invoice 数量金额匹配。
12. **PGL-V12（缺失）** 无部分收货与部分发票校验。
13. **PGL-V13（缺失）** Invoice 路由无权限。
14. **PGL-V14（缺失）** 软 remark 无 FK 完整性。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchases.id` | 全链 PO 锚点 |
| `po_no` | PO 业务号 |
| `supplier_id` | PO/Invoice/AP 供应商来源 |
| `total_amount` | Invoice/AP 金额来源 |
| `purchases.status` | Draft/Open/Received 等 |
| `purchase_items.purchase_id` | PO 行归属 |
| `qty/cost_price/amount` | 订购数量、成本和行金额 |
| `inventory_ledger.trans_type` | PO Receipt 表示收货 |
| `inventory_ledger.remark` | `PO-{id}` 软链接 |
| `inventory_ledger.qty` | 实际写入的收货增量 |
| `purchase_receipts` | 未使用的结构化 GR 表 |
| `purchase_invoices.purchase_id` | Invoice→PO |
| `purchase_invoices.invoice_amount` | PO 头金额镜像 |
| `ap_records.invoice_id` | AP→Invoice |
| `ap_records.supplier_id` | PO 供应商镜像 |
| `treasury_payment_records.supplier_id` | 付款供应商，未连 AP |

## 状态词汇

| 对象 | 状态 |
|---|---|
| PO | Draft、Open/Pending、Received/Completed |
| Invoice | Unpaid；Partial/Paid 未推进 |
| AP | Unpaid；无活动关闭 |
| GR | `PO Receipt` ledger 类型，无独立状态机 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| PGL-E01 | PO/行/receipt/invoice/AP DDL | 强 | `runtime/v14/legacy_support.py` |
| PGL-E02 | Receive 双写和幂等 | 强 | `apps/procurement/services.py`、`repository.py` |
| PGL-E03 | 发票/AP 创建链 | 强 | `apps/finance/services.py` |
| PGL-E04 | Invoice 路由无权限 | 强 | `apps/finance/router.py` |
| PGL-E05 | Received 后 UI 开票 | 中 | `templates/purchase_detail.html`、`purchase360.html` |
| PGL-E06 | AP 来源诚实说明 | 强 | `templates/ap_dashboard.html` |
| PGL-E07 | 三单匹配列为 gap | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| PGL-E08 | Purchase 收货报告 | 强 | `docs/reports/Business_Strong_A004_Purchase_Report.md` |
| PGL-E09 | 采购跨模块规格 | 弱/意图 | `business_modules/procurement.md` |

## UNKNOWN + 已查路径

1. **purchase_receipts 历史是否曾被写入 UNKNOWN。** 已查路径：DDL、Procurement/Inventory writers、backups。
2. **purchases 与 purchase_orders 迁移策略 UNKNOWN。** 已查路径：tenant schema、BI dataset、context360。
3. **Receive 是否业务上必须先 Approve UNKNOWN。** 已查路径：V18 docs、services、templates。
4. **PO 头金额何时保证与行汇总一致 UNKNOWN。** 已查路径：detail service、add/edit line。
5. **生产是否存在部分收货扩展 UNKNOWN。** 已查路径：receipt DDL、routes、imports。
6. **Invoice/AP 1:1 是否有 DB 约束 UNKNOWN。** 已查路径：DDL/indexes/migrations。
7. **软 remark 被人工修改后的追溯修复 UNKNOWN。** 已查路径：ledger edit routes、reports。
8. **tenant_id 是否贯穿 PO/ledger/invoice/AP UNKNOWN。** 已查路径：v41 schema、queries。
9. **三单匹配是否由外部 ERP 执行 UNKNOWN。** 已查路径：integrations、business_modules、reports。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
