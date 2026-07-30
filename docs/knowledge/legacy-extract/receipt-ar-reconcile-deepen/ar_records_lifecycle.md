# DO Post AR 后的 ar_records 生命周期

## Scope与证据强度

本页深化 Delivery Order Type A “Post AR” 后 `ar_records` 的初值、状态、余额和后续写入口。Post 路径为强证据；创建后的状态/余额更新与 Receipt 勾兑未找到。Post AR 是应收权责记录，不是税务或商业发票。

## 业务规则（稳定ID）

1. **ARL-R01** DO invoice Type A 是 Post AR 人工确认页。
2. **ARL-R02** GET 页面要求 AR.view 或 Delivery Orders.view。
3. **ARL-R03** POST 批准要求 AR.add 或 Delivery Orders.edit。
4. **ARL-R04** POST 必须 action=approve 且 human_confirm=1。
5. **ARL-R05** Inventory service 调 Finance `_legacy_create_ar(do_id)`。
6. **ARL-R06** Post 前必须找到 DO。
7. **ARL-R07** ar_records.customer_id 来自 DO。
8. **ARL-R08** customer_name 是 Post 时客户名称快照。
9. **ARL-R09** source_no 保存 DO 号，不保存 SO id 或 DO id 外键。
10. **ARL-R10** ar_date 使用 SQL 当天日期。
11. **ARL-R11** amount 等于 DO.total_amount。
12. **ARL-R12** 初始 balance 等于 amount。
13. **ARL-R13** 初始 status 固定 Unpaid。
14. **ARL-R14** Post 不写 paid_amount、due_date 或 ar_no。
15. **ARL-R15** Post 不更新 DO/SO 状态或 SO 收款镜像。
16. **ARL-R16** 同 DO 已有 AR 只在确认页警告，can_approve 仍为真。
17. **ARL-R17** 服务端无 source_no 幂等检查，DB 无唯一约束。
18. **ARL-R18** 未 Ship 的 DO 也只是 warning，不是 Post 阻断。
19. **ARL-R19** Post 是单 INSERT 后 commit，无显式 begin/rollback。
20. **ARL-R20** Receipt 写入不更新 ar_records.balance/status。
21. **ARL-R21** 应用层未找到 UPDATE ar_records，创建后 balance/status 实际冻结。
22. **ARL-R22** Receivable Center 读取 ar_records；open 口径通常排除 Closed。
23. **ARL-R23** Finance intelligence 的 future_ar 对 Unpaid balance 求和。
24. **ARL-R24** NDE Statement/Invoice 可读取 ar_records，但打印不等于状态推进。

## 流程

1. 用户从 DO 详情打开 invoice/Post AR。
2. 系统构造 Type A 确认上下文，并统计同 source_no 的历史 AR。
3. 即使已有记录或 DO 未 Ship，页面只显示 warning。
4. 用户提交 approve + human_confirm=1。
5. 权限通过后调用 Finance service。
6. 读取 DO 与客户，插入 Unpaid AR：amount=balance=DO total。
7. commit 后重定向 AR Dashboard。
8. 后续收款走 SO→receipts，不触碰该 AR 行。

## 校验（强/弱/缺失）

1. **ARL-V01（强）** DO 必须存在。
2. **ARL-V02（强）** action 必须 approve。
3. **ARL-V03（强）** human_confirm 必须为 1。
4. **ARL-V04（强/权限）** GET 要 AR.view 或 DO.view。
5. **ARL-V05（强/权限）** POST 要 AR.add 或 DO.edit。
6. **ARL-V06（弱/UI）** 重复 source_no 有 warning。
7. **ARL-V07（缺失）** 服务端不阻止重复 Post。
8. **ARL-V08（缺失）** source_no 无唯一约束。
9. **ARL-V09（缺失）** 未要求 DO 已 Ship。
10. **ARL-V10（缺失）** 未验证 DO total_amount 为正。
11. **ARL-V11（缺失）** 未验证客户存在/Active。
12. **ARL-V12（缺失）** 未写 due_date 或信用期。
13. **ARL-V13（缺失）** 未见 balance/status 合法更新状态机。
14. **ARL-V14（缺失）** 收款后不核对或关闭 AR。
15. **ARL-V15（缺失）** 重复行不做 reconciliation。

## 数据含义

| 数据 | Legacy 含义 |
|---|---|
| `ar_records.id` | 应收记录主键 |
| `ar_no` | 可空编号；Post 不填 |
| `customer_id` | DO 客户 |
| `customer_name` | Post 时名称快照 |
| `source_no` | 来源 DO 号 |
| `ar_date` | Post 当天日期 |
| `amount` | 原始应收额，等于 DO total |
| `balance` | 初始未收额，创建后无活动递减 |
| `status` | 初始 Unpaid |
| `paid_amount` | ar_records 未建模/未写 |
| `due_date` | ar_records 未建模/未写 |
| `create_time/close_time` | 补丁可能增加的 timeline 列，Post 不填 |
| `delivery_orders.total_amount` | AR 金额来源 |
| `receipts.so_id` | 收款关联 SO，不关联 AR |
| `sales_orders.payment_status` | 收款镜像，与 AR status 独立 |
| `future_ar` | Unpaid ar_records.balance 汇总 |
| `ar_already` | 确认页重复记录计数 |
| `can_approve` | 即使重复也保持可 Post |

## 状态词汇

| 词汇 | 含义 |
|---|---|
| Unpaid | Post AR 初始状态 |
| Open | 部分页面的开放项词汇 |
| Partial / Paid / Closed | UI 可显示，但 ar_records 写入口未找到 |
| Posted | AR 已插入，不是税票已开 |
| Received | 采购域状态 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| ARL-E01 | DO invoice GET/POST 和权限 | 强 | `apps/inventory/router.py` |
| ARL-E02 | Type A 上下文、重复 warning、human confirm | 强 | `apps/inventory/services.py` |
| ARL-E03 | ar_records INSERT 字段与 commit | 强 | `apps/finance/services.py` |
| ARL-E04 | ar_records DDL 无 paid/due/FK | 强 | `runtime/v14/legacy_support.py` |
| ARL-E05 | Type A 确认模板 | 强 | `templates/do_invoice.html` |
| ARL-E06 | Receivable Center 读取 ar_records | 强 | `apps/finance/repository.py`、`templates/receivable_center.html` |
| ARL-E07 | Receipt 只更新 receipts/SO | 强（负证据） | `apps/finance/services.py`、`repository.py` |
| ARL-E08 | Statement/NDE 读取 AR 行 | 强 | `document/nde_engine.py` |
| ARL-E09 | V18 报告声明 Post AR 非 tax invoice | 强 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| ARL-E10 | A-011 记录 AR 页面边界与缺口 | 强 | `docs/reports/Business_Strong_A011_AR_Ops_Report.md` |

## UNKNOWN + 已查路径

1. **ar_records.status 何时变 Partial/Paid/Closed UNKNOWN。** 已查路径：apps/finance、inventory、sales、triggers。
2. **paid_amount/due_date 是否计划加入 ar_records UNKNOWN。** 已查路径：DDL、upgrade_patch、business_modules、reports。
3. **重复 Post 是否在生产形成重复行 UNKNOWN。** 已查路径：warning、INSERT、DDL；未读取生产数据。
4. **ar_no 编号生成规则 UNKNOWN。** 已查路径：Post service、DDL、scripts、NDE fallback。
5. **receivables 表与 ar_records 的权威关系 UNKNOWN。** 已查路径：legacy_support、Finance services、templates。
6. **Post AR 是否应联动 DO/SO status UNKNOWN。** 已查路径：Inventory service、Shipment spec、V18报告。
7. **多 DO 对一 SO 时收款如何分配 UNKNOWN。** 已查路径：receipts、ar_records、allocation/reconcile 搜索。
8. **timeline 补丁字段是否由外部任务填写 UNKNOWN。** 已查路径：upgrade_patch、jobs、audit。
9. **Post 失败是否存在重试/补偿 UNKNOWN。** 已查路径：apply_do_invoice、exception handling、scheduler。

## 只读来源路径

- `H:\Workspace\EZAM_CRM - 9.0\apps\inventory\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\document\nde_engine.py`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\v14\legacy_support.py`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
