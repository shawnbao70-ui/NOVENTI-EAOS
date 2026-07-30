# AP Records 生命周期

## Scope与证据强度

本页核验 `ap_records` 的产生、状态、余额、到期和终止路径。运行 SQL/DDL 为强证据；`accounts_payable` 仅见规格和租户补丁名单。交叉引用 [`../finance/ap_payment_clearing.md`](../finance/ap_payment_clearing.md)。

## 业务规则（稳定ID）

1. **APL-R01** 运行态 AP 表为 `ap_records`。
2. **APL-R02** `accounts_payable` 未找到 CREATE TABLE 或活动 repository。
3. **APL-R03** AP 只随 `create_purchase_invoice` 创建，不可在 Dashboard 自由创建。
4. **APL-R04** 一 PO 一采购发票由 service 事前查重。
5. **APL-R05** 创建采购发票时同步插入同额 AP。
6. **APL-R06** 发票与 AP 初始 `paid_amount=0`、`balance_amount=amount`、`status=Unpaid`。
7. **APL-R07** AP amount 取 PO 头 `total_amount`。
8. **APL-R08** AP supplier_id 复制 PO 供应商。
9. **APL-R09** AP date 是创建日，不是 PO 日期或到期日。
10. **APL-R10** AP Dashboard 汇总直接读取静态 balance_amount。
11. **APL-R11** Treasury future_ap 只汇总 status=Unpaid 的 balance。
12. **APL-R12** 未找到 UPDATE/DELETE ap_records。
13. **APL-R13** 未找到付款后更新 purchase_invoices。
14. **APL-R14** `ap_records` 没有 due_date。
15. **APL-R15** Partial/Paid 仅由模板兼容展示，未见活动写入。
16. **APL-R16** UI 仅在 Received 后显示开票，但服务端不校验 Received。
17. **APL-R17** 发票/AP 双写同连接、一次 commit，无显式 transaction wrapper 证据。
18. **APL-R18** AP 列表发票引用显示 invoice_id，不是 invoice_no。

## 流程

1. PO 创建并形成头金额。
2. 用户触发采购发票创建。
3. Service 验证 PO 存在且尚无发票。
4. 同步写 `purchase_invoices` 与 `ap_records`。
5. 两者均初始化为 Unpaid/全额余额。
6. Dashboard 读取 AP；Treasury 付款走另一条链。
7. 无更新、关闭、删除或冲销，生命周期停在 Unpaid。

## 校验（强/弱/缺失）

1. **APL-V01（强）** PO 必须存在。
2. **APL-V02（强/应用）** 同 PO 不得重复发票。
3. **APL-V03（强）** AP Dashboard 要求 Finance.view。
4. **APL-V04（缺失）** create_purchase_invoice 路由无权限 gate。
5. **APL-V05（弱/UI）** Received 后才显示开票按钮。
6. **APL-V06（缺失）** 服务端不验证 PO Received。
7. **APL-V07（缺失）** 不验证发票金额与 PO 行/收货。
8. **APL-V08（缺失）** paid_amount/balance/status 无推进校验。
9. **APL-V09（缺失）** 无 due date 或账龄校验。
10. **APL-V10（缺失）** 无删除、作废、冲销保护。
11. **APL-V11（部分）** 双写共享 commit，但无显式事务边界。
12. **APL-V12（缺失）** DB UNIQUE/FK 约束未见。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `ap_records.id` | AP 行主键 |
| `invoice_id` | 指向 purchase_invoices.id |
| `supplier_id` | 从 PO 复制的供应商 |
| `ap_date` | AP 创建日 |
| `amount` | 原始应付额 |
| `paid_amount` | 初始 0，主链不更新 |
| `balance_amount` | 初始全额，Dashboard 口径 |
| `status` | 初始 Unpaid |
| `purchase_invoices.invoice_no` | PINV 时间戳系统号 |
| `purchase_invoices.purchase_id` | PO 来源 |
| `purchase_invoices.invoice_amount` | 从 PO 头复制金额 |
| `purchases.total_amount` | AP 金额来源 |
| `future_ap` | 未付 AP 余额汇总 |
| `accounts_payable` | 规格/补丁中的幻影表名 |

## 状态词汇

| 状态 | 实际语义 |
|---|---|
| Unpaid | 唯一活动写入状态 |
| Partial | 模板兼容词，未见写入 |
| Paid | 模板兼容词，未见写入 |
| Closed/Voided | 未见 AP 实现 |

## 证据表

| ID | 证据 | 强度 | 只读来源路径 |
|---|---|---|---|
| APL-E01 | ap_records DDL | 强 | `runtime/v14/legacy_support.py` |
| APL-E02 | purchase_invoices DDL | 强 | `runtime/v14/legacy_support.py` |
| APL-E03 | 发票+AP 双写 | 强 | `apps/finance/services.py` |
| APL-E04 | 创建路由无权限 | 强 | `apps/finance/router.py` |
| APL-E05 | Dashboard 汇总 | 强 | `apps/finance/services.py`、`templates/ap_dashboard.html` |
| APL-E06 | 付款不触 AP | 强 | `apps/finance/services.py`、`repository.py` |
| APL-E07 | 收货与开票 UI | 中 | `templates/purchase_dashboard.html`、`purchase_detail.html` |
| APL-E08 | A-020 AP 诚实性报告 | 强 | `docs/reports/Business_Strong_A020_AP_Ops_Report.md` |
| APL-E09 | accounts_payable 规格名 | 弱/冲突 | `business_modules/finance.md` |

## UNKNOWN + 已查路径

1. **生产 AP 是否被外部脚本更新 UNKNOWN。** 已查路径：全库 UPDATE/DELETE、jobs、scripts。
2. **accounts_payable 是否在旧租户库存在 UNKNOWN。** 已查路径：DDL、v41 tenant schema、repositories。
3. **purchase_id 是否有 DB UNIQUE UNKNOWN。** 已查路径：DDL、indexes、migrations。
4. **ap_records 是否有 DB FK UNKNOWN。** 已查路径：DDL、migration scripts。
5. **Partial/Paid 是否由外部集成写入 UNKNOWN。** 已查路径：finance/integrations/import。
6. **到期日是否在外部供应商系统维护 UNKNOWN。** 已查路径：AP DDL、Supplier、Finance。
7. **删除采购发票是否应级联 AP UNKNOWN。** 已查路径：Finance/Procurement delete routes。
8. **双写失败时 rollback 行为 UNKNOWN。** 已查路径：connection wrapper、service commit。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\procurement\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
