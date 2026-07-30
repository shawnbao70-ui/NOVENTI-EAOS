# AR 红冲、取消与贷项（AR Credit / Cancel）— Legacy Knowledge

**Evidence strength:** Strong for positive Post AR and Receipt paths; strong negative for operational AR reversal, credit-note posting and refund  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页核对 DO→`ar_records` 正向 accrual 的对称取消、Credit Note、红冲、write-off、Receipt void/refund 及 SO payment mirror。Post AR 是 Human Confirm 后插入正数 Unpaid row；重复只提示、不阻断。未观察到负 AR、反向引用、Credit Note 入账、AR cancel/close 命令、Receipt 删除/void/refund 或与 Reopen 联动。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| ARC-R1 | DO invoice Type A 表面实际 Post AR | 不是税务发票 |
| ARC-R2 | Post AR POST 接受 AR add 或 Delivery Orders edit | 跨模块 OR 权限门 |
| ARC-R3 | POST approve 要求 human_confirm=1 | 人工确认 |
| ARC-R4 | DO 只需存在即可 Post AR | open DO 也只是 warning |
| ARC-R5 | Post AR 不要求 DO Complete/Shipped | accrual timing 宽松 |
| ARC-R6 | `ar_records` source_no 保存 DO number | 文本追溯 |
| ARC-R7 | amount 与 balance 都取 DO total_amount | 全额正向 accrual |
| ARC-R8 | 初始 status 固定 Unpaid | 无 due date/currency |
| ARC-R9 | 已有同 DO AR 时只显示 duplicate warning | can_approve 仍为 true |
| ARC-R10 | 再次确认会再插一条 AR | 无 unique/guard |
| ARC-R11 | Post AR commit 独立于 DO 状态 | 不回写 invoiced/post flag |
| ARC-R12 | DO Reopen 不撤销 AR | status-only |
| ARC-R13 | SO cancel/reopen 不撤销 AR | 无联动 |
| ARC-R14 | Receipt 路径按 SO 剩余余额新增全额收款 | 与 ar_records 分离 |
| ARC-R15 | Receipt insert 自行 commit | 现金记录先落库 |
| ARC-R16 | 随后 SO payment mirror 另行 commit | 两步可部分成功 |
| ARC-R17 | Receipt 汇总不减少 `ar_records.balance` | 双轨 AR 不勾兑 |
| ARC-R18 | 未见 receipt delete/void/refund/negative receipt command | 现金逆向缺失 |
| ARC-R19 | 未见 `UPDATE/DELETE ar_records` 的活动取消/红冲 writer | accrual 逆向缺失 |
| ARC-R20 | `CREDIT_NOTE` 仅文档类型/模板/NDE 表面 | 不证明财务过账 |
| ARC-R21 | `DEBIT_NOTE` 同样是文档 registry 类型 | 与 AR row 无连接 |
| ARC-R22 | AR Dashboard 以非 Closed balance 汇总 | 无已证关闭命令 |
| ARC-R23 | Customer AR 以 SO−Receipts 计算 | 忽略 ar_records |
| ARC-R24 | Reopen/return 后两个 AR 口径都不会自动反向 | 余额可继续显示 |
| ARC-R25 | 未见 write-off、bad debt、credit memo application | 只能标缺失 |
| ARC-R26 | EAOS 不得把打印 Credit Note 当作贷项已入账 | document ≠ posting |

## 3. Process

### 3.1 Positive Post AR

1. 用户打开 DO invoice Type A。
2. 页面统计同 source_no AR，仅用于 warning。
3. Human Confirm approve。
4. Finance 读取 DO/customer。
5. 插入 `ar_records(amount=balance=DO total, status=Unpaid)`。
6. commit 并跳转 AR Dashboard。

### 3.2 Receipt

1. 读取 SO 与 receipts sum。
2. 以剩余余额建立 receipt 并 commit。
3. 重新汇总 receipts。
4. 更新 SO received/balance/payment_status 并再次 commit。
5. `ar_records` 不参与。

### 3.3 Missing reversal

未观察到 `Select original AR/Receipt → reason/authorization → reverse row/negative event → update balance/status → issue Credit Note/refund → sync SO/DO → audit`。

## 4. Symmetry Matrix

| Positive fact | Expected inverse | Observed | Strength |
|---------------|------------------|----------|----------|
| AR Unpaid +amount/+balance | linked −amount or reversal row | none | Missing |
| duplicate Post AR | unique source gate | warning only | Weak |
| Receipt +amount | void/refund/negative receipt | none | Missing |
| SO Paid mirror | recompute after receipt reversal | no reversal trigger | Missing |
| DO Post AR | unpost on Reopen/return | none | Missing |
| Credit Note document | posting to AR balance | no linkage | Metadata-only |
| AR status Unpaid | Closed/Cancelled/Reversed transition | no active writer found | Missing |

## 5. Validation

| ID | Validation | Strength |
|----|------------|----------|
| ARC-V1 | DO 必须存在 | Hard |
| ARC-V2 | approve 必须 human_confirm | Hard |
| ARC-V3 | POST 需 AR add 或 Delivery Orders edit | Hard at entry |
| ARC-V4 | DO 必须 shipped/complete | Missing；warning only for open |
| ARC-V5 | 同 source_no 只能一条 AR | Missing |
| ARC-V6 | AR amount 必须正且等于 eligible amount | Weak/direct copy |
| ARC-V7 | reversal 必须引用原 AR | Missing |
| ARC-V8 | credit amount 不得超过 outstanding | Missing |
| ARC-V9 | Receipt void/refund 必须引用原 receipt | Missing |
| ARC-V10 | Receipt 与 SO mirror 必须同事务 | Missing；separate commits |
| ARC-V11 | Receipt 必须 settle ar_records | Missing |
| ARC-V12 | Reopen/return 前必须检查财务影响 | Missing |
| ARC-V13 | status change 必须记录 actor/reason/time | Missing |
| ARC-V14 | Credit Note 必须受权限并过账 | Missing |

## 6. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| DO invoice Type A | AR accrual confirmation |
| `ar_records.customer_id/name` | accrual party snapshot |
| `ar_records.source_no` | DO number 文本 |
| `ar_records.ar_date` | posting date |
| `ar_records.amount` | 正向应收额 |
| `ar_records.balance` | 初始等于 amount，Receipt 不更新 |
| `ar_records.status=Unpaid` | 初始标签 |
| AR duplicate count | UI warning 数值，不是 guard |
| `receipts` | SO-linked positive cash event |
| `receipts.amount` | 剩余 SO balance |
| `receipts.currency=USD` | 活动路径默认 |
| SO `received_amount` | Receipts 汇总镜像 |
| SO `balance_amount` | total−receipts 镜像 |
| SO `payment_status` | Partial/Paid 收款进度 |
| Customer AR | SO totals minus Receipt sums |
| Receivable Center | `ar_records` 独立列表 |
| `CREDIT_NOTE` | 文档类型注册 |
| credit/reversal source ID | 未建模 |
| refund/void state | 未建模 |
| write-off reason | 未建模 |

## 7. State Vocabulary

| State / term | Meaning |
|--------------|---------|
| Unpaid | 新 AR 默认状态 |
| Closed | Dashboard 排除词；活动 transition 未证实 |
| Paid/Partial | SO 收款镜像状态 |
| Credit Note | 文档类型，不是 AR transition |
| Cancelled/Reversed/Voided/Refunded | 未见 canonical writer |
| duplicate warning | 允许继续 Post |

## 8. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 生产 AR 是否有人工 Closed writer | finance routes/services/repository/templates |
| 负数 ar_records 是否由私有入口允许 | runtime schema/finance writers |
| Credit Note 是否由未挂载 Print Center 之外服务过账 | document/NDE/finance/bootstrap |
| Receipt refund/void 的生产入口 | finance routes/residual/templates |
| Receipt 删除后 SO mirror 如何重算 | finance repository/service |
| AR 与 Receipts 的正式 reconciliation | finance/customer AR/reports |
| Duplicate AR 的清理策略 | finance scripts/reports |
| DO Reopen 后财务冲销政策 | inventory/finance/sales |
| bad debt/write-off 的审批与会计处理 | finance/approval/treasury |

## 9. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/inventory/services.py` | DO invoice context、duplicate warning、Post AR 调用 |
| `apps/inventory/router.py` | Type A route/permissions |
| `templates/do_invoice.html` | Human Confirm 表面 |
| `apps/finance/services.py` | `_legacy_create_ar`、Receipt flow |
| `apps/finance/repository.py` | Receipt separate commits、AR list/read |
| `apps/finance/router.py` | Finance active routes |
| `apps/finance/receipt_ar_expense_pages.py` | residual Finance surfaces |
| `runtime/v14/legacy_support.py` | AR/Receipt schemas、document registry |
| `document/nde_engine.py` | Credit Note document semantics |
| `templates/documents/credit_note.html` | 打印模板 |
| `templates/receivable_center.html` | AR 状态展示 |
| `templates/receipts.html` | Receipt list，无 reversal action |
| `business_modules/finance.md` | spec/runtime 差异 |
| `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` | Post AR honesty |
| `docs/reports/Residual_Decomposition_Vol026_Report.md` | Receipt/AR owner |
| `docs/knowledge/legacy-extract/finance/receipts_ar.md` | EAOS 只读交叉引用 |
| `docs/knowledge/legacy-extract/finance/ar_receipt_reconciliation.md` | EAOS 双轨 AR 交叉引用 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above（最后两项为 EAOS 只读交叉引用）。
