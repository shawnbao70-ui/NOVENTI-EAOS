# Approval Center 深化索引

## 文档导航

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`approval_center_runtime.md`](approval_center_runtime.md) | 运行时路由/表/状态机 | `ACR-*` |
| [`v18_vs_center.md`](v18_vs_center.md) | V18 Human Confirm vs 中央审批 | `VHC-*` |
| [`multi_step_evidence.md`](multi_step_evidence.md) | 多级/多步审批证据 | `MSE-*` |
| [`business_hook_gaps.md`](business_hook_gaps.md) | Quote/SO/Convert/Ship 挂钩缺口 | `BHG-*` |

## 交叉引用（只读，不改邻包）

| 邻包 | 权威主题 |
|---|---|
| [`../governance/approval.md`](../governance/approval.md) | Approval Center 治理总览 |
| [`../quote-convert-policy-deepen/approve_convert_policy.md`](../quote-convert-policy-deepen/approve_convert_policy.md) | Approve vs Convert 政策 |
| [`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md) | Quote Type A Approve |
| [`../order-chain/so_convert.md`](../order-chain/so_convert.md) | Convert SO |
| [`../order-chain/so_approve_open.md`](../order-chain/so_approve_open.md) | SO Approve→Open |

## 核心结论

1. 活动 Approval Center hub 是 `GET /approvals`；批准/拒绝是 **GET 写操作**，主路径写 `approval_history`，备用 `*_record` 路径不写历史。
2. 运行时表以 `approval_types` / `approval_records` / `approval_history` 为主；另有早期并行结构与 `approval_settings` / `approval_delegation` DDL，未见活动执行消费。
3. 状态机可观察为 `Pending` → `Approved` | `Rejected`；更新 **不校验** 原状态 Pending，也 **不校验** 操作者=指定 approver。
4. `create_approval()` 仅在 `runtime/v14/legacy_support.py`（及 backup）定义；全库业务 handler **无调用点**。
5. V18 Human Confirm 是业务模块本地 Type A 门（Quote/SO/PO/Ship/AR），不写也不读 Approval Center 记录。
6. Workflow 注册的 single/multi/sequential/parallel/conditional 审批全部 `implemented=false`；无多级步骤表执行证据。
7. Quote Approve、Convert、SO Approve、Ship **均不**提交或消费中央审批；Integration Queue 明确标为 No chain hook。

## 主要证据路径

- `apps/approval/router.py` · `services.py` · `repository.py` · `routes.py` · `approval_api.py` · `v14_residual.py`
- `runtime/v14/legacy_support.py`（DDL、`create_approval`、角色辅助）
- `core/workflow/approval.py` · `core/workflow/types.py` · `apps/workflow_center/approval_registry.py`
- `templates/approvals.html` · `approval_detail.html` · `approval_*.html`
- `business_modules/approval.md`
- `APPROVAL_WORKFLOW_MIGRATION_S013.md`
- `docs/reports/Business_Strong_A022_Approval_Ops_Report.md`
- `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md`
- `docs/reports/V18_SO_DO_Invoice_TypeA_Report.md`
- `docs/reports/Integration_Queue.md`
- `apps/quotation/services.py` · `apps/sales/services.py` · `apps/inventory/services.py`
