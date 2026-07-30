# V18 Human Confirm vs 中央审批差异

## Scope 与证据强度

本页对照两套并行机制：**V18 Type A Human Confirm**（业务页本地确认推进状态）与 **Approval Center**（横向 `approval_records` 决策）。强结论：二者数据结构、路由、审计与业务副作用均不同；未见自动互写。交叉引用 [`../governance/approval.md`](../governance/approval.md)（不改邻包）。

## 业务规则（稳定 ID）

1. **VHC-R01** Quote Approve：Draft + 有行 + `human_confirm=1` → `Sent`；写本地操作日志；不写 Approval Center。
2. **VHC-R02** SO Approve：pending stage + 有行 + `human_confirm=1` → `Open`；不写 Approval Center。
3. **VHC-R03** PO Approve：Draft + 有行 + `human_confirm=1` → `Open`；不写 Approval Center（见 procurement 证据链）。
4. **VHC-R04** DO Ship：open/未发运/库存/ledger + `human_confirm=1` → 出库；不进入中心待办。
5. **VHC-R05** DO→AR / AR Reminder 等同属 Type A Human Approved 面，不创建 `approval_records`。
6. **VHC-R06** Approval Center Approve 只改审批记录状态/结果/时间（+主路径历史），**不**推进 Quote/SO/PO/DO。
7. **VHC-R07** Hub 诚实边界：不静默创建 PO、SO、付款或发货（A-022）。
8. **VHC-R08** `human_confirm` 是请求表单位（`"1"`），不是审批人身份，不是多级步骤完成。
9. **VHC-R09** Approval Center 指定 `approver` 字符串；V18 本地门用模块权限（Quotes/Sales/Inventory edit 等），模型不同。
10. **VHC-R10** V18 决策路由为业务模块 POST Type A；中心决策为 Approval GET。
11. **VHC-R11** V18 成功直接改业务状态列；中心成功不回调业务列。
12. **VHC-R12** 宪章/报告中的 Human First 与 Automation Ladder「Human Approved」终点，**不得**等同中央 Approved。
13. **VHC-R13** `quote_approval` 辅助表与 Type A / 中心 records 均分离；未见主链消费者。
14. **VHC-R14** V18 报告明确 SO Approve / DO Ship / Post AR 为 additive Layer C，不改写 convert/ship 业务核心，也不声明中心挂钩。
15. **VHC-R15** 中心 UI「human confirm」是浏览器 `confirm`；V18 是服务端校验的 `human_confirm` 字段——同名不同强度。

## 对照矩阵

| 维度 | V18 Human Confirm | Approval Center |
|---|---|---|
| 载体 | 业务表 status + form `human_confirm` | `approval_records` / `approval_history` |
| 典型路由 | `/quotes/.../approve`、`/sales_order/{id}/approve`、`/delivery_order/{id}/ship` | `/approvals`、`/approve/{id}`、`/reject/{id}` |
| HTTP | Type A POST（业务） | GET 写 |
| 成功副作用 | 改业务状态/库存/AR | 仅改审批记录（主路径+历史） |
| 审批人模型 | 模块 RBAC + 操作者 | 记录上 `approver`（未强制校验） |
| 多级 | 无 | 元数据未实现 |
| AI | 可展示 warning；不自动批准 | Hub 声明无 AI auto-approve |

## 校验（强/弱/缺失）

1. **VHC-V01（强）** Quote Approve 强制 `human_confirm=="1"`。
2. **VHC-V02（强）** SO Approve 强制 `human_confirm=="1"`。
3. **VHC-V03（强）** Ship 强制 `human_confirm=="1"`。
4. **VHC-V04（强）** Quote/SO Approve 不调用 `create_approval` / 不读 `approval_records`。
5. **VHC-V05（强）** Center approve service 不更新 quotes/sales_orders/delivery_orders。
6. **VHC-V06（强）** 全库 `create_approval(` 调用点仅定义处（legacy_support + backup）。
7. **VHC-V07（缺失）** V18 成功不要求中心 Approved。
8. **VHC-V08（缺失）** 中心 Approved 不要求/不触发 V18 状态推进。
9. **VHC-V09（弱）** 中心列表 `onclick=confirm` 非服务端令牌。
10. **VHC-V10（强）** V15 报告：handlers never call `create_approval()`。

## 数据含义

| 数据 | 含义（诚实口径） |
|---|---|
| `human_confirm` | Type A 表单确认值；本地门输入 |
| `action=approve` | 业务 Type A 尝试推进 |
| `v18_human_confirm_required` | 缺少确认时的 flash/错误键 |
| `can_approve`（业务上下文） | UI 派生：阶段+有行等，非中心身份 |
| `approval_records.approval_status` | 中心 Pending/Approved/Rejected |
| `approval_records.approver` | 中心指定审批人用户名 |
| `approval_history` | 中心决策审计（主路径） |
| Quote `Sent` | V18 本地发布结果 |
| SO `Open` | V18 本地订单释放结果 |
| Hub「Human Approved」提示文案 | 交互诚实提示，不是 DB 状态 |
| `quote_approval` | 报价辅助表，非中心 records |
| 操作日志「V18 Type A Human Approved」 | 本地动作日志，非中心 history |
| `approval_result` | 中心决策结果字段 |
| Automation Ladder Human Approved | 宪章/产品语义终点，≠表状态 |

## 状态词汇

| 术语 | 层 | 是否互通 |
|---|---|---|
| Draft→Sent | Quote V18 | 否→中心 |
| pending→Open | SO V18 | 否→中心 |
| Pending→Approved | Approval Center | 否→业务 |
| Human Approved | Type A / Ladder | 非中心状态 |
| Rejected（中心） | Approval Center | 不映射业务拒收/取消 |

## 证据表

| ID | 观察事实 | 强度 | 只读来源路径 |
|---|---|---|---|
| VHC-E01 | Quote Approve human_confirm 门 | 强 | `apps/quotation/services.py` |
| VHC-E02 | SO Approve human_confirm 门 | 强 | `apps/sales/services.py` |
| VHC-E03 | Ship/Invoice human_confirm 门 | 强 | `apps/inventory/services.py` |
| VHC-E04 | Center approve 只改 records+history | 强 | `apps/approval/services.py` |
| VHC-E05 | create_approval 无业务调用 | 强 | 全库 `create_approval(` grep；`legacy_support.py` |
| VHC-E06 | V18 Type A 报告范围 | 强 | `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` |
| VHC-E07 | V15：approval 未强制接入 | 强 | `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` |
| VHC-E08 | governance 双机制定义 | 强 | `../governance/approval.md` |
| VHC-E09 | Hub confirm vs 服务端令牌差 | 强/弱 | `templates/approvals.html` |
| VHC-E10 | quote_approval helper 分离 | 强 | `apps/quotation/utils.py` |

## UNKNOWN + 已查路径

1. **部署插件是否在网关层把 V18 与中心串联 UNKNOWN。** 已查：apps/approval、quotation、sales、inventory、bootstrap 相关报告。
2. **历史环境是否曾用 `add_test_approval` 人工造数联调 UNKNOWN。** 已查：A-022、S013 deferred、templates。
3. **`quote_approval` 是否有外部脚本/报表消费者 UNKNOWN。** 已查：quotation utils/facade、approval apps、templates。
4. **中心 Rejected 是否应映射业务取消的正式意图 UNKNOWN。** 已查：approval services、business_modules、V15/V18 reports。
5. **Finance 付款 Type A 与 PAYMENT 类型种子的预期挂钩 UNKNOWN。** 已查：approval seeds、finance services、Integration_Queue。
6. **同一用户名在 V18 actor 与中心 approver 是否应强制一致 UNKNOWN。** 已查：router username、services actor、repository pending filter。

## 只读来源路径汇总

`apps/quotation/services.py` · `apps/sales/services.py` · `apps/inventory/services.py` · `apps/approval/services.py` · `apps/quotation/utils.py` · `templates/approvals.html` · `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md` · `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` · `docs/reports/Business_Strong_A022_Approval_Ops_Report.md` · `../governance/approval.md` · `runtime/v14/legacy_support.py`
