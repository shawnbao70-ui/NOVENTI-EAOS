# Approval Center 深化包

## 目的

本包核验 Legacy **Approval Center** 的运行时路由、表与状态机，并与 **V18 Human Confirm** 本地门、多级/多步审批元数据、以及 Quote Approve / SO Approve / Convert / Ship 业务挂钩缺口做证据对照。它只记录可执行事实，不把 Workflow 注册元数据、`approval_settings` 种子值、或业务模块规格中的目标路由解释为已实施能力。

## 边界

- 横向治理总览继续以 [`../governance/approval.md`](../governance/approval.md) 为权威；本包深化运行时与挂钩缺口，**不修改**该邻包正文。
- Quote Approve / Convert 政策继续参考 [`../quote-convert-policy-deepen/`](../quote-convert-policy-deepen/) 与 [`../quotation-deepen/`](../quotation-deepen/)。
- SO Convert / Approve / DO 链继续参考 [`../order-chain/`](../order-chain/)。
- 本包不开启 CRUD、不自开 G、不触碰 Brain/Twin、不改代码或根级 STATUS/CHANGELOG。

## 内容

| 文档 | 主题 |
|---|---|
| [`approval_center_runtime.md`](approval_center_runtime.md) | 路由、表、Pending→Approved/Rejected 状态机 |
| [`v18_vs_center.md`](v18_vs_center.md) | V18 Human Confirm vs 中央审批差异 |
| [`multi_step_evidence.md`](multi_step_evidence.md) | 多级/多步/并行/条件审批证据有无 |
| [`business_hook_gaps.md`](business_hook_gaps.md) | 与 Quote/SO/Convert/Ship 的挂钩缺口 |
| [`INDEX.md`](INDEX.md) | 稳定 ID 与证据索引 |

## 证据口径

- **强**：活动路由、`apps/approval` service/repository、DDL、模板与报告相互印证。
- **弱**：UI `confirm`、模块规格目标路径、种子设置、残留双注册。
- **缺失**：业务 handler 未调用 `create_approval`；Workflow `implemented=false`；无业务回调。
- **Human Approved ≠ Approval Center Approved**：前者是 Type A 表单确认位；后者是 `approval_records.approval_status`。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`

必查面：`apps/approval/`、`governance` 邻包、`templates/approval*`、`business_modules/approval.md`、`docs/reports/`（含 A-022、V15、V18）、`core/workflow/approval.py`、`runtime/v14/legacy_support.py`。
