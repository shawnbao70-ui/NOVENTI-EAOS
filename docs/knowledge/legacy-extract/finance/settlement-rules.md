# 结算规则（Commission / Settlement Rules）— Legacy Knowledge

**Evidence strength:** Medium — commission ledger and level rates are observable; approval and payout closure are weak  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0` (read-only)

---

## 1. 范围与证据强度

Legacy 中不存在字面名为“结算规则”或 `settlement_rule` 的独立模块。最接近且具备规则、计算和台账的数据域是 **Commission Center / Commission360**，即销售提成、佣金、TC 台账和返利结算。

该能力横跨 Sales 与 Finance：

- Sales 维护销售员、职级并在报价转销售订单时触发提成计算；
- Finance 边界声明拥有 commission、TC ledger 与 rebate；
- `commission_rules` 是界面展示的规则主数据；
- 实际自动计算使用 `sales_levels.commission_rate`，两者没有可观察到的关联；
- 计算结果停留在 `Pending` 台账，未形成批准、付款或工资集成闭环。

报价付款条件、AR/AP 收付状态和 GFIP 分期计划属于相邻的**支付条款/账款结清**语义，已在应收应付与发票文件中记录；它们不是本文件所指的 Commission 结算规则。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外 / 缺口 | EAOS 重写备注 |
|----|----------|----------|-------------|----------------|
| SR-R1 | 运行时提成费率取销售员所属职级的 `commission_rate` | 报价转销售订单 | Commission Center 中维护的 `commission_rules` 不参与计算 | 规则展示与执行必须统一 |
| SR-R2 | 订单转化时的提成基数为销售订单总额 | 创建销售订单成功 | 另一演示计算器按已回款额计算，口径冲突 | 规则必须显式声明基数 |
| SR-R3 | 提成金额 = 结算基数 × 提成率 ÷ 100，并按两位小数记录 | 生成 TC 台账 | 未见币种、税、舍入尾差规则 | 保存币种和计算快照 |
| SR-R4 | 只有订单关联销售员且销售员能关联职级时，才取得有效费率 | 报价转订单 | 无职级时费率可能退化为 0 | 缺失规则应告警而非静默归零 |
| SR-R5 | 新台账来源类型为 Sales Order，来源号为 SO 编号，状态固定 `Pending` | 提成计算成功 | 未发现后续 Approved/Paid 流转 | 建立明确结算状态机 |
| SR-R6 | 提成写入失败不阻断销售订单创建 | 转订单期间异常 | 失败会被静默忽略，形成漏记 | 订单成功与结算失败应通过可靠事件解耦并可重试 |
| SR-R7 | 默认职级 A/B/C 分别配置 30%/25%/20% 提成率，并带月目标和标准 TC 奖励 | 初始化 Legacy 数据 | 费率较高且只是种子数据，不能视为企业通用政策 | 迁移时保留“配置事实”，不要默认启用 |
| SR-R8 | Commission Center 可维护规则名称、提成比例和备注 | 人工新增规则 | 规则没有生效期、优先级、适用范围，也不参与自动计算 | 改为版本化可执行规则 |
| SR-R9 | Commission 周期只用于列表展示 | 查看周期 | 未约束计算日期、关账或跑批 | 周期需参与结算范围与锁定 |
| SR-R10 | 演示提成计算器按已回款金额 × 提成率计算，并单独计算回款率 | 测试/计算器路径 | 与生产订单总额口径不一致 | 不得作为正式结算结果 |
| SR-R11 | 返利由人工填写客户、项目、接收人、类型和金额，初始状态 `Pending` | 新增返利 | 不与订单、回款、规则或审批自动联动 | 返利应作为独立结算类型 |
| SR-R12 | 菜单通常只向 Admin/Manager 显示 Commission Management | 导航 | 多数相关路由未执行同等级权限检查 | 菜单隐藏不能替代服务端鉴权 |
| SR-R13 | Commission Center 页面需 Commission Center 的查看权限 | 进入中心 | 权限目录使用 `Commission`，命名不一致 | 统一 RBAC 资源标识 |
| SR-R14 | 蓝图提出固定、阶梯、利润、产品、区域、品牌、团队及周期奖励等规则 | 产品设计意图 | Legacy 9.0 未观察到这些规则的执行引擎 | 标为未来需求，不迁移为现状 |
| SR-R15 | AI 可以辅助计算，但最终结算应由企业审批 | 治理要求 | 运行代码只写 Pending，未接审批 | 人类批准应成为硬门槛 |
| SR-R16 | 经销商页面可展示 commission/settlement 载荷，但明确不自动结算 | 经销商查看 | 与销售员佣金台账无自动关系 | 不把展示载荷视为结算事实 |

---

## 3. 流程

### 3.1 订单触发提成

1. 报价经确认后转为销售订单。
2. 系统检查订单是否关联销售员。
3. 通过销售员的 `level_id` 查找销售职级。
4. 读取职级提成率。
5. 以订单总额计算提成金额。
6. 写入 `tc_ledger`，状态为 `Pending`。
7. 继续复制订单行并完成订单创建；提成失败不阻断主交易。

### 3.2 规则与人员维护

1. Commission Center 列出 `commission_rules`。
2. 可直接提交规则名称、提成比例和备注。
3. 销售员维护时绑定职级，并从职级复制月度目标。
4. 职级页面可查看默认职级；新增职级路径的持久化实现未生效。
5. 规则表与职级费率之间没有自动同步。

### 3.3 台账查看

1. TC Ledger 按销售员与销售订单展示销售额、费率、提成金额和状态。
2. Commission Periods 展示周期数据，但不参与筛选或关账。
3. 未观察到台账审核、驳回、支付、冲销或重算操作。

### 3.4 返利登记

1. 人工填写客户、项目、接收人、返利类型、金额和备注。
2. 建立状态为 `Pending` 的返利记录。
3. 未观察到后续审批、付款或与 TC 台账合并。

### 3.5 演示计算路径

1. 读取或构造订单额、已回款额与提成率。
2. 计算回款率。
3. 按已回款额计算提成金额。
4. 写入 `salesperson_commissions`，供计算器和排名展示。
5. 该路径与正式 TC 台账并行，不能视为同一结算口径。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| SR-V1 | 报价不得重复转为销售订单 | Hard | 间接降低重复提成风险 |
| SR-V2 | Commission Center 访问需查看权限 | Hard at page | 其他结算路由不一致 |
| SR-V3 | 新增规则的名称与比例为必填 | Form-level | 未见业务范围校验 |
| SR-V4 | 提成率必须在 0–100% | Missing | 可负数或超过 100 |
| SR-V5 | 规则必须有生效期与失效期 | Missing | 无版本控制 |
| SR-V6 | 规则必须定义适用人员/产品/区域/组织 | Missing | 当前执行仅依赖职级 |
| SR-V7 | `commission_rules` 与职级费率一致 | Missing | 展示与执行可能冲突 |
| SR-V8 | 同一来源订单只能有一条有效 TC 台账 | Missing / indirect only | 仅依靠报价转订单防重 |
| SR-V9 | 台账从 Pending 到 Approved/Paid 必须审批 | Missing | 未发现状态更新 |
| SR-V10 | 结算周期锁定后不得重算 | Missing | 周期未参与计算 |
| SR-V11 | 提成失败必须可见、可重试 | Missing | 当前静默忽略 |
| SR-V12 | 新增销售职级可持久化 | Broken / incomplete | 路由存在但写入未生效 |
| SR-V13 | 返利金额必须为正且有业务来源 | Missing | 仅表单必填 |
| SR-V14 | 所有结算路由统一鉴权 | Missing | 菜单、目录和页面权限名不一致 |

---

## 5. 数据含义

### 5.1 规则与人员

| Entity / Field | Legacy 含义 |
|----------------|-------------|
| `commission_rules.rule_name` | 展示用规则名称 |
| `commission_rules.commission_rate` | 展示/手工维护的比例，未接入主计算 |
| `sales_levels.level_code` / `level_name` | 销售职级标识与名称 |
| `sales_levels.monthly_target` | 职级月度销售目标 |
| `sales_levels.commission_rate` | 主计算实际读取的职级提成率 |
| `sales_levels.standard_reward_tc` | 标准 TC 奖励；具体兑换意义未实现 |
| `salespersons.level_id` | 销售员绑定职级 |
| `salespersons.monthly_target` | 创建销售员时从职级复制的目标 |
| `salespersons.current_tc` | 当前 TC；未观察到自动更新 |
| `salespersons.achievement_rate` | 达成率；未观察到自动计算 |

### 5.2 TC 台账

| Field | 含义 |
|-------|------|
| `salesperson_id` | 提成归属销售员 |
| `source_type` | 来源类型，主路径固定为 Sales Order |
| `source_no` | 销售订单编号 |
| `sales_amount` | 计算时的订单金额 |
| `commission_rate` | 计算时使用的费率快照 |
| `commission_amount` | 计算结果 |
| `status` | 初始 `Pending`；未观察到状态流转 |
| `create_time` | 台账建立时间 |

### 5.3 并行/预留实体

| Entity | 含义与成熟度 |
|--------|--------------|
| `salesperson_commissions` | 演示计算与排名明细，按回款额计算，与 TC 台账并行 |
| `commission_periods` | 结算周期主数据，只读展示 |
| `commission_policy` | 包含奖励率、低价阈值、标准 TC 等字段；无活动业务引用 |
| `commissions` | 通用佣金预留表；未观察到读写 |
| `rebates` | 人工返利记录，初始 Pending |

### 5.4 状态语义

| Status | 使用位置 | 含义 |
|--------|----------|------|
| `Pending` | TC 台账、返利、通用佣金 | 待处理；未形成可确认的后续状态机 |
| `Active` | 销售职级、销售员 | 当前有效；未观察到完整停用流程 |

### 5.5 TC 的不确定含义

`standard_reward_tc`、`current_tc` 与 `tc_ledger` 表明 TC 是奖励/积分型结算单位，但 Legacy 未提供兑换、计价、到期或支付规则，因此不能断言 TC 等同现金佣金。

---

## 6. 只读来源路径

| Path | Why cited |
|------|-----------|
| `Business_Module_Registry.md` | Sales/Finance 对 commission、TC ledger、rebate 的边界声明 |
| `apps/sales/services.py` | 报价转订单时触发提成计算 |
| `apps/sales/repository.py` | 职级费率读取与 TC 台账写入 |
| `apps/sales/v14_residual.py` | Commission Center、职级、销售员、计算器、周期、排名、返利路径 |
| `templates/commission_center.html` | 规则列表字段与页面语义 |
| `templates/tc_ledger.html` | TC 台账展示语义 |
| `templates/includes/v11/legacy_menu.html` | Admin/Manager 菜单可见性 |
| `core/permission/module_catalog.py` | Commission 权限目录 |
| `runtime/v14/legacy_support.py` | 规则、职级、销售员、周期、佣金、TC、返利实体 |
| `docs/reports/V15_ENTERPRISE_READINESS_REPORT.md` | Commission Center 部分就绪的项目自评 |
| `docs/constitution/volume-02-eaos/BOOK07.md` | 佣金透明、AI 可计算、最终结算需企业批准 |
| `docs/project/_blueprint_extracts/NOVENTI_AI_GIOS_Master_Blueprint_V4新版项目书.txt` | 阶梯/利润/区域/团队提成、返利和自动结算设计意图 |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
