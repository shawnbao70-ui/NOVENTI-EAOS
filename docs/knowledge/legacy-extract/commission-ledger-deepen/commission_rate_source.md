# 佣金费率来源（Commission Rate Source）— Legacy Knowledge

**Evidence strength:** Strong for level-based runtime lookup; strong negative for executable Commission Center rules  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. Scope 与证据强度

本模块描述 canonical 佣金费率如何从 `salespersons.level_id` 关联到 `sales_levels.commission_rate`，并区分 `commission_rules`、`commission_policy`、SO 可选字段和演示 calculator 等平行规则源。

运行时 lookup 证据强；Commission Center 规则只被新增和展示，未接入 Quote→SO 计算。新增 sales level 的 INSERT 被注释，故页面存在但持久化不完整。

---

## 2. Business Rules

| ID | Rule / observed boundary | Evidence / consequence |
|----|--------------------------|------------------------|
| CRS-R1 | canonical rate 来自 salesperson 对应 level | 不是订单表单输入 |
| CRS-R2 | lookup 使用 salesperson→sales_levels 左连接 | level 缺失时仍可返回空费率 |
| CRS-R3 | 缺失 level/rate 退化为 0 | 不阻断 SO 转换 |
| CRS-R4 | rate 被解释为百分数，计算时除以 100 | 30 表示 30% |
| CRS-R5 | 默认种子等级 A/B/C 费率分别为 30/25/20 | 是 Legacy 配置事实，不是企业政策建议 |
| CRS-R6 | 默认等级同时含 monthly target 和 standard reward TC | 这些字段不参与 canonical 金额公式 |
| CRS-R7 | 新建 salesperson 必须提交 level ID | 服务端未验证 level 必须存在 |
| CRS-R8 | salesperson monthly target 在创建时从 level 复制 | 后改 level target 不自动同步 |
| CRS-R9 | salesperson status 默认 Active | canonical lookup 未检查 status |
| CRS-R10 | sales level status 未参与佣金 lookup | Inactive level 仍可能提供 rate |
| CRS-R11 | Commission Center `commission_rules` 可新增名称、费率、备注 | 只是平行展示主数据 |
| CRS-R12 | `commission_rules.commission_rate` 不参与 canonical lookup | 规则展示与执行分裂 |
| CRS-R13 | `commission_policy` 含 reward/threshold 等预留字段 | 未观察到活动读取 |
| CRS-R14 | `commissions.commission_rate` 是另一预留台账字段 | 未观察到 canonical 写入 |
| CRS-R15 | calculator 使用固定 3% 样例 | 不代表 salesperson level rate |
| CRS-R16 | 新增 sales level 路由接收 rate，但实际 INSERT 被注释 | 表单成功返回不代表已保存 |
| CRS-R17 | 未观察到 level/rule 编辑、版本或生效期 | 历史规则治理缺失 |
| CRS-R18 | `tc_ledger` 保存实际 rate 快照 | 后改等级不会改变旧台账 |
| CRS-R19 | rate 没有产品、区域、客户、毛利、回款或周期维度 | canonical 只有 salesperson level |
| CRS-R20 | EAOS 不得以 Commission Center rule 推断实际执行费率 | 权威执行源是 sales level lookup |
| CRS-R21 | `sales_orders.commission_rate/commission_amount` 列虽存在，但 convert 不写入 | 不可作为订单级权威费率 |
| CRS-R22 | `distributor_levels.commission_rate` 属分销商平行域 | 不驱动 salesperson TC ledger |
| CRS-R23 | legacy helper 可按 collection amount 计算佣金 | 与 canonical SO-total 基数冲突，未接主链 |
| CRS-R24 | salesperson、sales level 和 TC ledger 页面未见独立权限门 | 配置与快照可见性治理不足 |

---

## 3. Process

### 3.1 业务员与等级配置

1. 系统初始化 A/B/C 等级及费率。
2. 新建 salesperson 时选择 level。
3. 系统查询 level monthly target 并复制到 salesperson。
4. level 不存在时 target 退化为零，仍可建立 salesperson。

### 3.2 转单费率解析

1. 从 SO 读取 salesperson ID。
2. 通过 salesperson.level_id 左连接 sales_levels。
3. 读取 commission_rate；无结果时使用 0。
4. 将该 rate 用于金额计算并快照到 `tc_ledger`。

### 3.3 平行规则维护

Commission Center 可新增 `commission_rules`，但 canonical calculation 不查询该表。新增 sales level 表单则未完成实际写入，导致“展示规则可新增、执行等级难维护”的不对称。

---

## 4. Validation

| ID | Validation | Strength | Detail |
|----|------------|----------|--------|
| CRS-V1 | salesperson 创建必须提供 level_id | Form required | |
| CRS-V2 | level_id 必须存在 | Missing | 不存在仍可建人 |
| CRS-V3 | salesperson 必须 Active 才计佣 | Missing | lookup 不看 status |
| CRS-V4 | sales level 必须 Active 才计佣 | Missing | lookup 不看 status |
| CRS-V5 | commission rate 必须 0–100 | Missing | 无范围门 |
| CRS-V6 | rate 不得为空 | Weak | 空值归零 |
| CRS-V7 | level_code 必须唯一 | Weak / seed only | INSERT OR IGNORE 不等于 schema unique 已证 |
| CRS-V8 | rule 必须有生效期/失效期 | Missing | schema 无字段 |
| CRS-V9 | rule 必须绑定 level/人员/产品/区域 | Missing | `commission_rules` 无适用域 |
| CRS-V10 | Commission Center rule 必须与执行 rate 一致 | Missing | 两表无同步 |
| CRS-V11 | 新 sales level 必须持久化 | Broken | INSERT 被注释 |
| CRS-V12 | rate 变更必须保留版本与批准人 | Missing | 无 history/audit |

---

## 5. Data Semantics

| Entity / field | Honest Legacy meaning |
|----------------|-----------------------|
| `salespersons.id` | 佣金受益人主键 |
| `salespersons.level_id` | canonical rate lookup 关联 |
| `salespersons.status` | Active 等人员标签；lookup 不检查 |
| `salespersons.monthly_target` | 创建时从 level 复制的目标快照 |
| `salespersons.current_tc` | 当前 TC 预留值，未见自动更新 |
| `salespersons.achievement_rate` | 达成率预留值，未见自动计算 |
| `sales_levels.level_code` | A/B/C 等级代码 |
| `sales_levels.level_name` | 等级名称 |
| `sales_levels.commission_rate` | canonical 执行百分比 |
| `sales_levels.monthly_target` | 等级月目标 |
| `sales_levels.standard_reward_tc` | 标准 TC 奖励配置 |
| `sales_levels.bonus_rate` | 奖金率预留，canonical 不读 |
| `sales_levels.status` | 等级状态标签，lookup 不读 |
| `commission_rules.commission_rate` | Commission Center 展示费率，不执行 |
| `commission_policy` | 未接入的复合政策预留 |
| `sales_orders.commission_rate` | 订单预留列；convert 未填充 |
| `distributor_levels.commission_rate` | 分销商等级费率，非 salesperson rate |
| `tc_ledger.commission_rate` | 计算时实际费率快照 |
| calculator 3% | 测试样例常量，非业务规则源 |

---

## 6. State Vocabulary

| Value / term | Meaning / caveat |
|--------------|------------------|
| Active salesperson | 新建默认状态；未成为 lookup gate |
| Active level | 种子状态；未成为 lookup gate |
| A / B / C | 默认销售等级代码 |
| Senior Sales / Sales / Junior Sales | 默认等级名称 |
| 30 / 25 / 20 | 种子百分比，不应无条件迁移为政策 |
| rate 0 | 缺失等级/费率的静默退化结果 |

---

## 7. UNKNOWN 与已查路径

| UNKNOWN | Paths searched |
|---------|----------------|
| 30/25/20 高费率是现金佣金还是 TC 奖励比例 | seed DDL、templates、reports、blueprint |
| 生产是否曾直接修改 sales_levels 数据 | sales routes/templates、admin/import scripts、reports |
| level status Inactive 的正式效果 | sales lookup、person pages、commission center |
| salesperson 改等级的活动入口 | sales routes/templates/repositories；未见 edit |
| commission_rules 的预期执行器 | sales/finance services、scheduler、AI/automation paths |
| commission_policy 的正式字段含义和使用者 | runtime DDL、full path searches、reports |
| rate 变更是否需要 Approval Center | sales/finance/approval paths；未见接线 |
| 多币种下 rate 是否不变、基数如何换算 | quotation currency、SO schema、finance locale paths |
| bonus_rate 与 standard_reward_tc 如何兑现 | sales level/TC ledger/payroll searches |
| SO 上预留 commission 字段的计划写者 | runtime schema、sales convert/update、finance paths |

---

## 8. Evidence Table

| Read-only path | Evidence |
|----------------|----------|
| `apps/sales/services.py` | 费率缺失退化与计算使用 |
| `apps/sales/repository.py` | salesperson→level lookup |
| `apps/sales/v14_residual.py` | 人员、等级、规则和 calculator 路由 |
| `runtime/v14/legacy_support.py` | levels/persons/rules/policy DDL 与种子 |
| `templates/new_salesperson.html` | level 必选表面 |
| `templates/salespersons.html` | 人员与 level 展示 |
| `templates/new_sales_level.html` | level/rate 表单表面 |
| `templates/commission_center.html` | rules 展示 |
| `templates/commission_calculator.html` | 固定样例平行口径 |
| `Business_Module_Registry.md` | Sales commission ownership 声明 |
| `business_modules/sales.md` | Sales 模块边界 |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | Commission Center partial/not-ready |
| `docs/reports/Business_Strong_A012_SO_Ops_Report.md` | SO conversion 事实背景 |
| `core/permission/module_catalog.py` | Commission RBAC 注册名 |
| `core/permission/checker.py` | 未观察到 Commission Center alias |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
