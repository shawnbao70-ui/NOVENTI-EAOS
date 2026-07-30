# Approval Submit Hooks Deepen

## 目的

本包从 **提交挂钩** 视角深挖 Legacy Approval Center：谁调用 `create_approval`、Quote/SO/Convert/Ship 是否写入中央 `approval_records`、多级步骤引擎是否可执行、以及 Center 批准/拒绝的 HTTP 方法与 CSRF 风险。它只记录可执行事实，不把 `business_modules/approval.md` 中的目标 POST/`submit_approval`、Workflow 注册元数据、或 Hub 导航链接解释为已接线提交闭环。

## 边界

- Approval Center 运行时/状态机权威继续以 [`../approval-center-deepen/`](../approval-center-deepen/) 为准；本包深化 **提交调用点与挂钩**，**不修改**该邻包正文。
- GET mutation / CSRF 总览继续参考 [`../command-authz-deepen/get_mutation_surface.md`](../command-authz-deepen/get_mutation_surface.md)；本包只固化 Approval Center 决策表面细节，**不修改**该邻包正文。
- 治理总览继续参考 [`../governance/approval.md`](../governance/approval.md)（只读交叉）。
- 不开启 CRUD、不自开 G、不触碰 Brain/Twin、不改代码或根级 STATUS/CHANGELOG/根 README。

## 内容

| 文档 | 主题 |
|---|---|
| [`create_approval_call_sites.md`](create_approval_call_sites.md) | `create_approval` / 提交审批全库调用点 |
| [`quote_so_ship_hooks.md`](quote_so_ship_hooks.md) | Quote/SO/Convert/Ship 是否创建中央审批记录 |
| [`multi_step_runtime.md`](multi_step_runtime.md) | 多级步骤表/引擎是否可执行（非 scaffold） |
| [`get_approve_reject_surface.md`](get_approve_reject_surface.md) | Center 批准/拒绝 HTTP 方法与 CSRF 风险 |
| [`INDEX.md`](INDEX.md) | 稳定 ID 与证据索引 |

## 证据口径

- **强**：活动路由、service/repository、DDL、全库符号检索、模板与报告相互印证。
- **弱**：UI `confirm`、模块规格目标路径、种子设置、残留双注册、旧表造数路由。
- **缺失**：业务 handler 未调用 `create_approval`；`submit_approval` POST 无运行时路由；Workflow `implemented=false`；无业务回调。
- **Human Approved ≠ Approval Center Approved**：前者是 Type A 表单确认位；后者是 `approval_records.approval_status`。
- **`create_quote_approval` ≠ `create_approval`**：前者写 `quote_approval` 辅助表；后者写中央 `approval_records`。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`

必查面：`apps/approval/`、`apps/quotation/`、`apps/sales/`、`apps/inventory/`、`apps/workflow_center/`、`core/workflow/`、`runtime/v14/legacy_support.py`、`templates/approval*`、`business_modules/approval.md`、`docs/reports/`（含 A-022、V15、Integration_Queue、S013）。
