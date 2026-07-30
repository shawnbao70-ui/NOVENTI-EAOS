# 生命周期链接钩子原子性（Lifecycle Hook Atomicity）— Legacy Knowledge

**Evidence strength:** Strong for post-commit placement and internal commits; strong negative for Convert blocking, retry and compensation  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

## 1. Scope 与证据强度

本页分析 `link_sales_order_from_quote` 如何把 Quote 的 `requirement_id` / `opportunity_id` 传播到 SO 和 Requirement，以及失败是否阻断 Convert。Canonical Sales 在 SO/TC/items/quote 主 commit 后调用该 hook，并在外层吞所有异常；hook 内部的安全读取可转为空结果，更新 helper 又自行 commit。因此它是 post-commit、best-effort、允许部分成功的追踪增强，不是 Convert 原子组成。

## 2. Business Rules

| ID | Rule / observed boundary | Consequence |
|----|--------------------------|-------------|
| LH-R1 | Convert 先提交 SO/TC/items/quote status | lifecycle 在商业事实之后 |
| LH-R2 | hook 接收同 cursor/connection、so_id、quote_id | 无独立事件 envelope |
| LH-R3 | hook 重新读取 quote 全行 | 不使用前面 Convert 的 quote snapshot |
| LH-R4 | quote 不存在/读取失败时静默 return | SO 保持已提交 |
| LH-R5 | 只传播非空 requirement_id/opportunity_id | 空值不会清除 SO |
| LH-R6 | 只更新目标表实际存在的列 | schema-aware no-op |
| LH-R7 | SO trace 更新由 `_safe_update` 自行 commit | 独立于 Convert 主 commit |
| LH-R8 | 有 requirement 时再更新 business_requirements.sales_order_id | 第二个可独立 commit |
| LH-R9 | requirement_links 存在时尝试写关系行 | 第三层可选追踪 |
| LH-R10 | requirement_links 失败在 hook 内吞掉 | 前两层可能已成功 |
| LH-R11 | hook 整体异常在 Sales Convert 外层吞掉 | 不阻断 redirect |
| LH-R12 | lifecycle 缺失不改变 quote `已确认` | 用户表面仍看到成功 |
| LH-R13 | legacy Quotation 转换副本未观察到 hook | route owner 不同可产生追踪差异 |
| LH-R14 | 标准 bootstrap 由 Sales canonical owner | 通常会尝试 hook |
| LH-R15 | SO 无 trace 列时 update 成为 no-op | 不报 schema mismatch |
| LH-R16 | Requirement 无 downstream 列时同步成为 no-op | 不报完整性缺失 |
| LH-R17 | 无 outbox、retry count、failure status 或 dead-letter | 缺链不可自动恢复 |
| LH-R18 | 页面 enrich 也宽泛吞异常 | 缺链可能只表现为少上下文 |
| LH-R19 | requirement/opportunity 链接不是业务授权或审批 | 只作 traceability |
| LH-R20 | EAOS 不得用 SO 存在推定生命周期链接完整 | 必须逐层核验 |

## 3. Process 与失败矩阵

### 3.1 正常路径

1. Convert 主 SQL commit。
2. 读取 quote。
3. 从 quote 收集 requirement/opportunity。
4. 若 SO 有列，更新 SO 并 commit。
5. 若 requirement 存在且表有列，更新其 sales_order_id 并 commit。
6. 若 link 表存在，写 `from_quote` 关系。
7. 返回 Sales 列表。

### 3.2 Failure / no-op

| Failure point | Convert result | Trace result |
|---------------|----------------|--------------|
| quote read returns empty | Success | 全部缺失 |
| SO trace columns absent | Success | SO update no-op，后续 requirement 仍可能更新 |
| SO update raises | Success | 外层吞；后续步骤不执行 |
| requirement update raises | Success | SO 已 commit，requirement 未同步 |
| requirement_links insert raises | Success | SO/requirement 可能已 commit，link row 缺失 |
| legacy convert owner | Success | 未观察到任何 lifecycle hook |

## 4. Validation

| ID | Validation | Strength |
|----|------------|----------|
| LH-V1 | quote 必须可读取 | Weak/no-op |
| LH-V2 | target columns 必须存在 | Soft schema detection |
| LH-V3 | requirement/opportunity 非空才传播 | Hard branch |
| LH-V4 | hook 成功是 Convert 成功条件 | Missing/false |
| LH-V5 | SO、Requirement、link row 同事务 | Missing |
| LH-V6 | failure 必须写 durable event | Missing |
| LH-V7 | partial link 必须重试/补偿 | Missing |
| LH-V8 | quote trace 与 SO trace 必须一致 | Missing |
| LH-V9 | requirement_id/opportunity_id 必须有 FK integrity | UNKNOWN |
| LH-V10 | duplicate requirement link 必须唯一 | UNKNOWN |
| LH-V11 | legacy/canonical 路径必须同语义 | Missing |
| LH-V12 | 页面展示必须告警缺链 | Missing |

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `quotes.requirement_id` | Quote 上游需求追踪 |
| `quotes.opportunity_id` | Quote 上游机会追踪 |
| `sales_orders.requirement_id` | best-effort 复制结果 |
| `sales_orders.opportunity_id` | best-effort 复制结果 |
| `business_requirements.sales_order_id` | downstream 回链，若列存在 |
| `business_requirements.quote_id` | Quote 阶段回链 |
| `requirement_links` | 可选关系表 |
| link type `from_quote` | SO 关系来源标签 |
| `_table_columns` | schema capability 检查 |
| `_fetchone` empty dict | 读取失败/无记录的共同 no-op 表面 |
| `_safe_update` | 只写存在列并自行 commit |
| main Convert commit | hook 调用之前的商业提交 |
| lifecycle commit | post-commit 局部更新 |
| missing link | SO 有效但 trace 不完整 |
| partial link | SO trace、requirement back-link、relation row 仅部分存在 |
| enrich context | 页面读取增强，不修复持久化 |
| lifecycle failure event | 未建模 |
| retry state | 未建模 |

## 6. State Vocabulary

| Term | Meaning |
|------|---------|
| linked | 至少某一追踪字段已写，不自动代表全层完整 |
| unlinked | SO 存在但无 requirement/opportunity |
| partial link | 多层追踪事实不一致 |
| schema no-op | 目标列不存在而静默跳过 |
| post-commit best-effort | 失败不撤销 Convert |
| `from_quote` | requirement link 来源标签 |

## 7. UNKNOWN 与已查路径

| UNKNOWN | 已查路径 |
|---------|----------|
| 生产 sales_orders 是否都有 trace columns | runtime DDL、database migrations、lifecycle schemas |
| requirement_links 是否在所有部署存在 | lifecycle repository/schema、runtime |
| link row 是否有唯一约束 | lifecycle DDL/repository |
| partial link 是否有巡检/修复作业 | lifecycle jobs/scripts/reports |
| `_safe_update` 第一 commit 后第二步失败的告警 | workflow/log/audit paths |
| quote trace 在 Convert 同时被修改时采用哪个值 | sales/quotation services、locking/version |
| 非 Enterprise route 是否使用 legacy 无 hook 实现 | entrypoints/bootstrap/residual |
| 页面是否明确显示“追踪不完整” | sales/object360/lifecycle templates |
| requirement/opportunity 删除后的 referential policy | lifecycle/requirements/opportunity services |

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 主 commit 后调用并吞异常 |
| `apps/sales/repository.py` | quote commit 点 |
| `v15/business_lifecycle/workflow.py` | link 逻辑与 `_safe_update` commit |
| `v15/business_lifecycle/repository.py` | requirement_links 写入 |
| `v15/business_lifecycle/enrich.py` | 页面追踪读取 |
| `apps/quotation/quote_pages.py` | legacy convert 无 hook |
| `apps/quotation/v14_residual.py` | residual route |
| `runtime/v14/legacy_support.py` | quote/SO trace columns |
| `database/business_lifecycle_schema.py` | lifecycle schema 能力 |
| `bootstrap/enterprise_cutover.py` | canonical 挂载顺序 |
| `bootstrap/v14_residual.py` | residual conflict filter |
| `templates/sales_order_detail.html` | SO trace 展示表面 |
| `business_modules/sales.md` | Sales 边界 |
| `docs/reports/V151E_Volume009_Quotation_Sales_Business_Chain_Extraction_Report.md` | Quote→SO hook 抽取 |
| `docs/reports/V15_ENTERPRISE_INTELLIGENCE_REPORT.md` | lifecycle 追踪边界 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\`
