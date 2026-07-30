# 信用控制深化包

## 目的

本包核验 Legacy 中客户信用字段、暂停/失效标签、Quote→SO→DO→Ship 信用门禁，以及正式 override/bypass 是否存在。它只记录可执行事实，不把 UI 风险提示、AI 元数据、审批表或 DDL 预留字段解释为已实施信用控制。

## 边界

- 信用额度概览继续以 [`../commercial-terms/credit_limit.md`](../commercial-terms/credit_limit.md) 为权威。
- 客户状态和余额继续以 [`../customer-deepen/`](../customer-deepen/) 为权威。
- 报价转换政策继续参考 [`../quote-convert-policy-deepen/`](../quote-convert-policy-deepen/)。
- 本包只深化字段来源、硬/软门禁和绕过缺口，不修改邻包。

## 内容

- [`credit_limit_fields.md`](credit_limit_fields.md)：credit_limit、credit_level、payment_days 的结构与消费。
- [`status_pause_freeze.md`](status_pause_freeze.md)：暂停/失效/冻结/黑名单是否阻断交易。
- [`convert_ship_credit_gates.md`](convert_ship_credit_gates.md)：Convert、SO Approve、Create DO、Ship 门禁矩阵。
- [`override_bypass.md`](override_bypass.md)：特权、UI-only warning、无权限变更入口和正式 override 缺失。
- [`INDEX.md`](INDEX.md)：稳定 ID 与证据索引。

## 证据口径

- **强**：运行路由、service/repository、DDL、模板和报告相互印证。
- **弱**：UI 隐藏、warning、AI 标签、残留审批结构。
- **缺失**：无服务端信用比较、状态阻断、override 实体或审计。
- `Credit Watch` 不是 Credit Hold；`暂停跟进`/`失效客户` 是标签，不是交易冻结。

## 只读证据根

`H:\Workspace\EZAM_CRM - 9.0`
