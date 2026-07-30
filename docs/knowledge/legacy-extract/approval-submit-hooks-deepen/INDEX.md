# Approval Submit Hooks Deepen — 索引

## 文档导航

| 文档 | 主题 | 稳定 ID |
|---|---|---|
| [`create_approval_call_sites.md`](create_approval_call_sites.md) | create_approval / 提交调用点 | `CAS-*` |
| [`quote_so_ship_hooks.md`](quote_so_ship_hooks.md) | Quote/SO/Convert/Ship 挂钩 | `QSH-*` |
| [`multi_step_runtime.md`](multi_step_runtime.md) | 多级步骤运行时可执行性 | `MSR-*` |
| [`get_approve_reject_surface.md`](get_approve_reject_surface.md) | GET 批准/拒绝与 CSRF | `GAR-*` |

## 交叉引用（只读，不改邻包）

| 邻包 | 权威主题 |
|---|---|
| [`../approval-center-deepen/approval_center_runtime.md`](../approval-center-deepen/approval_center_runtime.md) | Center 路由/表/状态机 |
| [`../approval-center-deepen/business_hook_gaps.md`](../approval-center-deepen/business_hook_gaps.md) | Quote/SO/Convert/Ship 挂钩缺口 |
| [`../approval-center-deepen/multi_step_evidence.md`](../approval-center-deepen/multi_step_evidence.md) | 多级元数据 vs 执行 |
| [`../command-authz-deepen/get_mutation_surface.md`](../command-authz-deepen/get_mutation_surface.md) | GET mutation 总清单与 CSRF |
| [`../governance/approval.md`](../governance/approval.md) | Approval 治理总览 |
| [`../quotation-deepen/quote_approve.md`](../quotation-deepen/quote_approve.md) | Quote Type A Approve |
| [`../order-chain/so_convert.md`](../order-chain/so_convert.md) | Convert SO |
| [`../order-chain/so_approve_open.md`](../order-chain/so_approve_open.md) | SO Approve→Open |

## 核心结论

1. `create_approval()` **仅定义**于 `runtime/v14/legacy_support.py`（及 backup 镜像）；活动 `apps/**` 业务 handler **无调用点**；亦无运行时 `POST /submit_approval`。
2. `add_test_approval` 向旧表 `approvals` 造数，**不**调用 `create_approval`，**不**写 `approval_records`。
3. `create_quote_approval` 写 `quote_approval`，与中央 `create_approval` 分离；Type A Quote Approve **不**调用二者。
4. Quote Approve / Convert / SO Approve / Ship **均不**创建或消费中央审批记录；与 Integration Queue「No chain hook」及 V15「never called」一致。
5. Workflow `APPROVAL_TYPES` 五键全部 `implemented=false`；活动 Center 是单记录单次决策，**无**可执行多级步骤引擎。
6. Center `/approve/{id}`、`/reject/{id}`（及 `*_record`）均为 **GET 写**；CSRF middleware 将 GET 视为 SAFE；页面路由无 RBAC；UI `confirm` 可被直链绕过。

## 主要证据路径

- `runtime/v14/legacy_support.py`（`create_approval`、`can_create_approval`、DDL、种子）
- `apps/approval/router.py` · `services.py` · `repository.py` · `permissions.py` · `v14_residual.py`
- `apps/quotation/services.py` · `utils.py` · `facade.py`
- `apps/sales/services.py` · `router.py`
- `apps/inventory/services.py` · `router.py`
- `apps/supplier/v14_residual.py`（`/add_test_approval`）
- `core/workflow/approval.py` · `core/workflow/types.py` · `apps/workflow_center/approval_registry.py`
- `core/security/csrf.py` · `core/security/middleware.py`
- `core/capabilities/approval/service.py`（能力壳，无提交实现）
- `templates/approvals.html` · `approval_detail.html`
- `business_modules/approval.md`
- `APPROVAL_WORKFLOW_MIGRATION_S013.md`
- `docs/reports/Business_Strong_A022_Approval_Ops_Report.md`
- `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md`
- `docs/reports/Integration_Queue.md`
