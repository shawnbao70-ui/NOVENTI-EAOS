# Quote Convert Policy Deepen — Legacy Knowledge Pack

## Purpose

本包对 EZAM_CRM 9.0 的报价状态、批准与转单门禁、并发幂等及商务条款传播进行知识抽取。内容描述可证 Legacy 行为与缺口，不复制源码，也不将目标架构、模板文案或表名推测为运行事实。

## Modules

- [`quote_state_normalization.md`](quote_state_normalization.md)：中英状态 writer/reader/KPI 分裂及不可安全等价关系。
- [`approve_convert_policy.md`](approve_convert_policy.md)：Quote Approve、Convert、状态旁路和中央审批的独立边界。
- [`convert_concurrency.md`](convert_concurrency.md)：一报价一 SO 防重、并发 race、事务和副作用原子性。
- [`commercial_term_propagation.md`](commercial_term_propagation.md)：付款、信用、折扣、FX、税和 Incoterms 的转单传播断点。
- [`INDEX.md`](INDEX.md)：证据强度、跨包关系与覆盖门槛索引。

## Evidence Posture

1. **Strong**：活动 service/repository/router、运行 schema、模板实际消费字段。
2. **Medium**：bootstrap、business modules 与工程报告用于解释 owner/边界。
3. **Strong negative**：在规定目录和关键词检索后，目标校验、约束或传播字段未出现。
4. **UNKNOWN**：无法由静态只读证据确认的运行部署、产品意图或异常恢复行为。

## Critical Honesty Findings

- Sent、Won 与 `已确认` 分别代表本地发布、手工成交标签和转单写回，不能按语言直接合并。
- Quote Approve 可被直接状态更新或 Convert 绕过；中央 Approval Center 未成为 Quote/SO 的前置门。
- “一报价一 SO”主要是先查后插，没有已证实的数据库唯一约束或 idempotency token。
- 佣金和 lifecycle 是不同强度的转单副作用：佣金异常可导致已提交 SO 缺台账，lifecycle 在提交后 best-effort。
- Quote 的 currency、rate、validity、payment、delivery、remark 不随 Convert 进入 SO；SO/Receipt/AR 的币种和账期链不完整。

## Hard Boundaries

- 本包不赋予任何 CRUD、批准、转单、付款或治理能力。
- Human Approved 不等于中央多级审批。
- AI/提示/摘要只作顾问证据，不执行业务动作，不涉及 Brain/Twin。
- 仅写 `docs/knowledge/legacy-extract/quote-convert-policy-deepen/**`。

## Read-only Roots

- `H:\Workspace\EZAM_CRM - 9.0\apps\quotation\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\sales\`
- `H:\Workspace\EZAM_CRM - 9.0\apps\finance\`
- `H:\Workspace\EZAM_CRM - 9.0\templates\`
- `H:\Workspace\EZAM_CRM - 9.0\business_modules\`
- `H:\Workspace\EZAM_CRM - 9.0\docs\reports\`
- `H:\Workspace\EZAM_CRM - 9.0\runtime\`
- `H:\Workspace\EZAM_CRM - 9.0\bootstrap\`
- `H:\Workspace\EZAM_CRM - 9.0\v15\business_lifecycle\`
