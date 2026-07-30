# Invoice / PO / GR 三单匹配

## Scope 与结论

本页深化 [`../ap-payment-deepen/ap_po_gr_link.md`](../ap-payment-deepen/ap_po_gr_link.md)，不重复采购与财务权威。结论：Legacy 有 `PO → purchase_invoice → ap_record` 结构链，也有 `PO → inventory_ledger` 收货软链，但没有把三者汇合成数量、价格、金额和容差校验；这不是“三单匹配”。

## 业务规则（稳定 ID）

1. **IPG-R01** 开票入口按 `purchase_id` 读取 `purchases` 头。
2. **IPG-R02** PO 不存在时返回采购列表，不产生 Invoice/AP。
3. **IPG-R03** Service 以 `purchase_invoices.purchase_id` 事前查重，一 PO 最多创建一张采购发票。
4. **IPG-R04** 上述一对一是应用层判重；DDL 未给 `purchase_id` UNIQUE。
5. **IPG-R05** `invoice_amount` 直接取 `purchases.total_amount`，不从收货流水重算。
6. **IPG-R06** Invoice 的 supplier 直接复制 PO 的 `supplier_id`。
7. **IPG-R07** Invoice 创建日和 `PINV` 编号来自服务器时间。
8. **IPG-R08** 新 Invoice 初始化 `paid=0`、`balance=invoice_amount`、`status=Unpaid`。
9. **IPG-R09** 同一流程同步建立同额、同 supplier 的 `ap_records`。
10. **IPG-R10** 活动 GR 事实是 `inventory_ledger.trans_type='PO Receipt'` 与 `remark='PO-{id}'`。
11. **IPG-R11** `purchase_receipts` 虽有 DDL，但活动 Receive 路径不写它。
12. **IPG-R12** Invoice 不存 receipt/ledger 外键，也没有发票行。
13. **IPG-R13** 服务端开票不要求 PO 为 Received，也不读取收货 ledger。
14. **IPG-R14** UI 仅在 Received 后显示 Create Invoice，属于展示门槛，不是服务端门槛。
15. **IPG-R15** 开票路由为 GET，未见 Finance/Treasury 权限检查或 Human Confirm。
16. **IPG-R16** Receive 是全量 PO 行过账；没有 received/remaining 数量供三单匹配。
17. **IPG-R17** PO 行的 qty/cost/amount 不复制到 Invoice，无法逐行做 qty/price variance。
18. **IPG-R18** 无 tolerance、exception queue、match status 或差异审批。
19. **IPG-R19** Invoice 与 AP 两次 INSERT 后统一 commit；该局部链预期同事务提交。
20. **IPG-R20** 正式报告把三单匹配列为未完成能力，不能从 UI 名称推断其存在。

## 实际流程与缺失汇合点

1. PO 头与行建立，头保存 `total_amount`。
2. Receive 将有效行数量写入库存、产品镜像与 `PO Receipt` ledger，并把 PO 标记 Received。
3. 开票动作只重新读取 PO 头并按 `purchase_id` 查重。
4. 它不读取 PO 行、`purchase_receipts` 或 `inventory_ledger`。
5. Invoice 与 AP 按 PO 头总额初始化。
6. 因此“已开票”只能证明 PO 头被镜像，不能证明货已收、数量相符或价格相符。

## 校验（强 / 弱 / 缺失）

1. **IPG-V01（强）** PO 必须存在。
2. **IPG-V02（强/应用层）** 同 `purchase_id` 已有 Invoice 时拒绝重复创建。
3. **IPG-V03（强）** Receive 检查 PO 存在及未处于 received stage。
4. **IPG-V04（强）** Receive 检查 `PO Receipt + PO-{id}` ledger 幂等事实。
5. **IPG-V05（强）** Receive 至少需一条有效行并能取得库存行。
6. **IPG-V06（弱/UI）** Received 后才显示开票操作。
7. **IPG-V07（缺失）** 服务端不校验 PO status=Received。
8. **IPG-V08（缺失）** 不校验至少存在一条 GR/ledger。
9. **IPG-V09（缺失）** 不校验 PO qty = GR qty = Invoice qty。
10. **IPG-V10（缺失）** 不校验 PO price = Invoice price。
11. **IPG-V11（缺失）** 不校验 Invoice 总额与 PO 行汇总。
12. **IPG-V12（缺失）** 无 tax/freight/discount/rounding 差异处理。
13. **IPG-V13（缺失）** 无匹配容差与超差审批。
14. **IPG-V14（缺失）** `remark` 软链接无 FK/不可变约束。
15. **IPG-V15（缺失）** 开票 GET 路由无权限与抗 CSRF 的写动作门槛。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `purchases.id` | PO 主键，也是跨链锚点 |
| `purchases.total_amount` | Invoice/AP 的直接金额来源 |
| `purchases.supplier_id` | Invoice/AP 供应商来源 |
| `purchases.status` | Draft/Open/Received 等采购阶段 |
| `purchase_items.qty` | 订购量；未拆 ordered/received |
| `purchase_items.cost_price` | PO 行成本 |
| `purchase_items.amount` | PO 行金额 |
| `inventory_ledger.trans_type` | `PO Receipt` 表示收货过账 |
| `inventory_ledger.qty` | 单条入库增量，不是 Invoice qty |
| `inventory_ledger.remark` | `PO-{id}` 软 PO 引用 |
| `purchase_receipts` | 未被活动 Receive 使用的结构化 GR DDL |
| `purchase_invoices.purchase_id` | Invoice→PO 结构关联 |
| `purchase_invoices.invoice_amount` | PO 头总额快照 |
| `purchase_invoices.status` | 初始化 Unpaid；不是 match status |
| `ap_records.invoice_id` | AP→Invoice |
| match status/variance | 未建模 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| IPG-E01 | Invoice/AP 创建、金额复制、查重与 commit | 强 | `apps/finance/services.py` |
| IPG-E02 | 开票 GET 路由及权限缺口 | 强 | `apps/finance/router.py` |
| IPG-E03 | PO Receive、status 与 ledger 幂等 | 强 | `apps/procurement/services.py`、`repository.py` |
| IPG-E04 | Inventory ledger 写入字段 | 强 | `apps/inventory/repository.py` |
| IPG-E05 | PO/行/receipt/invoice/AP DDL | 强 | `runtime/v14/legacy_support.py` |
| IPG-E06 | Received 后 UI 开票门槛 | 中 | `templates/purchase_detail.html`、`purchase360.html` |
| IPG-E07 | 三单匹配为已知 gap | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| IPG-E08 | AP 来源与人工付款边界 | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |
| IPG-E09 | 采购意图与运行事实对照 | 弱/意图 | `business_modules/procurement.md`、`business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **生产库是否有外部程序写 `purchase_receipts` UNKNOWN。** 已查：Procurement/Inventory/Finance writers、imports、jobs、DDL；未读生产库。
2. **PO 头总额是否始终等于行汇总 UNKNOWN。** 已查：PO add/edit/detail service、templates、repository。
3. **人工是否在系统外完成三单匹配 UNKNOWN。** 已查：reports、business_modules、Approval、templates。
4. **invoice number 是否应来自供应商票号 UNKNOWN。** 已查：Invoice 表单、route、service、DDL；当前为系统 `PINV`。
5. **同 PO 多张分批供应商发票的业务政策 UNKNOWN。** 已查：Invoice DDL、service 查重、reports。
6. **税、运费、折扣和汇率进入 PO 总额的政策 UNKNOWN。** 已查：purchase schema、pricing、finance。
7. **`PO-{id}` remark 被修改后的修复流程 UNKNOWN。** 已查：ledger edit/reversal routes、reports。
8. **多租户下 match 锚点是否包含 tenant UNKNOWN。** 已查：runtime DDL、queries、tenant schema。

## 只读来源路径

`apps/finance/`、`apps/procurement/`、`apps/inventory/`、`templates/`、`runtime/v14/legacy_support.py`、`business_modules/`、`docs/reports/`。
