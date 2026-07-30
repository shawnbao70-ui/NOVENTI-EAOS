# 库存（Inventory）— Legacy Knowledge

**Evidence strength:** Strong（页面服务、持久化、A-002/A-018）  
**Domain identity:** `inventory` 是现存量操作面，`inventory_ledger` 是变动审计，`products.stock_qty` 是 Legacy 镜像  
**Chain role:** Procurement Receive → Stock → Delivery Ship；另含手工调整与扫码动作  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

---

## 1. 范围

Legacy 可运行能力包括库存列表/详情、低库存、安全库存与自由文本库位、手工调整、库存台账、采购收货、发货出库和扫码仓动作。模块规格中的多仓、库位主数据、盘点单、库存预留、批次与序列号未观察到运行实现。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 | EAOS 重写备注 |
|----|----------|----------|-----------|---------------|
| I-R1 | 每个产品 SKU 可有一条库存记录，包含现存量、安全库存和库位 | 查看/过账 | 缺行时可从产品库存镜像建立 | 数据库约束一 SKU 一库存记录 |
| I-R2 | Edit 仅维护安全库存和库位，不允许改现存量 | 更新库存元数据 | 库位只是自由文本 | 数量变更必须走过账命令 |
| I-R3 | 手工调整以当前量加变动量计算新余额；变动不可为零，结果不可为负 | Adjust | 交易类型可由请求字符串带入 | 规范交易原因枚举 |
| I-R4 | 正规数量变更同时更新库存记录、产品库存镜像并追加台账 | Adjust/Receive/Ship | 多写路径分散在多个模块 | 建立单一库存过账服务 |
| I-R5 | 仅现存量为零时可删除库存记录；历史台账不删除 | Delete | | 优先停用而非删除 |
| I-R6 | 现存量不高于安全库存即为低库存 | KPI/补货 | `safe_stock=0` 时零库存也入选 | 策略参数化 |
| I-R7 | PO 收货增加库存，台账类型为 `PO Receipt`，并把 PO 置 Received | Receive | Draft 也被视为开放阶段 | 收货前硬校验已批准 |
| I-R8 | 创建 DO 不扣库存；DO Ship 才扣库存并写 `DO Ship` 台账 | Fulfillment | A-003 前历史数据可能已在创建时扣过 | 迁移时识别历史双扣 |
| I-R9 | Ship 要求 DO 开放且库存充足；相同 DO 台账存在时拒绝重复出库 | Ship | 应用层查重，非唯一约束 | 数据库幂等键 |
| I-R10 | DO Complete 只改履约状态；Reopen 也只回状态，绝不自动回补库存 | Complete/Reopen | 回补须人工 Adjust | 使用显式冲销交易 |
| I-R11 | 扫码 Receive/Ship/Move 复用采购收货、DO 出库和调整逻辑，并要求人工确认 | Scan action | 自动选择最近开放 PO/DO | 显式确认目标单据 |
| I-R12 | 低库存补货只生成 Draft PO；批准和收货是后续独立步骤 | Replenish | 补货本身不改库存 | 保持建议与过账分离 |
| I-R13 | AI 只提供建议，不允许静默修改库存 | 所有 AI 辅助界面 | | 保持人类授权 |
| I-R14 | 库存金额为现存量乘产品成本价 | 列表/KPI | 成本价与库存量来自不同表 | 明确估值时点与方法 |
| I-R15 | 产品编辑存在直接改 `products.stock_qty` 的旁路，不写库存记录或台账 | Product update | 可造成镜像漂移 | 禁止旁路写 |

---

## 3. 流程

### 3.1 手工调整

库存详情 → Adjust → 校验非零变动和非负结果 → 更新现存量 → 同步产品镜像 → 追加带结余台账 → 提交。

### 3.2 采购入库

开放 PO → Receive → 校验行项与重复台账 → 按行建立/取得库存记录 → 增加库存与镜像 → 写 `PO Receipt` → PO Received。

### 3.3 发货出库

SO 创建 DO（不扣库存）→ DO Ship 人工确认 → 校验开放阶段、幂等与逐行库存 → 扣库存与镜像 → 写 `DO Ship` → DO Shipped。

### 3.4 扫码仓动作

识别 SKU → 选择 Receive / Ship / Move → 人工确认 → 分派到采购收货、DO Ship 或 Transfer In/Out 调整。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| I-V1 | 调整量不可为零 | Hard | |
| I-V2 | 调整后余额不可为负 | Hard | |
| I-V3 | 删除库存记录要求现存量为零 | Hard | 不删台账 |
| I-V4 | PO 收货要求单据存在、开放、有行且未过账 | Hard | 开放阶段错误地包含 Draft |
| I-V5 | DO Ship 要求开放、库存充足且未过账 | Hard | |
| I-V6 | Complete 仅允许 Shipped；Reopen 仅允许 Complete | Hard | |
| I-V7 | 扫码仓动作要求 `human_confirm=1` | Hard | |
| I-V8 | Inventory view/edit/delete RBAC | Hard | 非标准 403 响应 |
| I-V9 | 安全库存不可为负 | Absent | 解析失败还会退为零 |
| I-V10 | 调整交易类型必须属于白名单 | Weak | 表单限制可被直接请求绕过 |
| I-V11 | `inventory.stock_qty` 与 `products.stock_qty` 必须一致 | Absent | 无约束、无对账任务 |
| I-V12 | 数量过账并发保护 | Absent | 无行锁、版本号或原子条件更新 |
| I-V13 | 多仓、批次、序列号、预留量 | Absent | 规格意图未落地 |
| I-V14 | 页面查询租户范围一致 | Weak/Unclear | 工具方法有 scope，页面 SQL 未显式体现 |

---

## 5. 数据含义

### 5.1 实体

| Entity | Meaning |
|--------|---------|
| `inventory` | SKU 现存量操作记录 |
| `inventory_ledger` | 追加式库存变动事实与过账后结余 |
| `products.stock_qty` | 供产品与旧路径读取的库存镜像 |
| `safe_stock` | 触发低库存的阈值 |
| `location` | 自由文本货位，不是仓库/库位主数据引用 |

### 5.2 台账字段

| Field | Meaning |
|-------|---------|
| `trans_type` | 变动业务类型 |
| `qty` | 本次变动；入库为正、出库为负 |
| `balance_qty` | 本次过账后的库存余额 |
| `remark` | 与 PO、DO、样品或手工调整关联的字符串 |
| `create_time` | Legacy 过账时间 |

### 5.3 观察到的交易类型

| Type | Direction | Source |
|------|-----------|--------|
| Manual Adjustment / Cycle Count | ± | 手工调整 |
| Damage Write-off | 通常为负 | 手工调整 |
| Transfer In / Transfer Out | ± | 扫码 Move |
| PO Receipt | 正 | 采购收货 |
| DO Ship | 负 | 发货出库 |
| Sample Receipt | 正 | 样品入库 |

---

## 6. 诚实缺口与风险

- **双写漂移：** 库存与产品各存一份数量，产品编辑可绕过库存台账。
- **并发超卖/重复过账：** 读取余额、计算、写回以及台账查重均缺少数据库级并发保护。
- **单据循环部分失败：** 多行收发在循环中写多个对象，事务边界依赖共享连接实现。
- **无库存预留：** DO 创建不锁库存，直到 Ship 才发现短缺。
- **无多仓模型：** `location` 不能表达仓库、库位、批次或调拨。
- **状态回退不冲销：** Reopen 不恢复库存，运营人员必须另做有理由的调整。
- **历史数据风险：** A-003 前 DO 可能已在创建时扣过产品库存，再走 Ship 可能形成双扣。

---

## 7. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/inventory/services.py` | 调整、DO Ship/Complete/Reopen、扫码动作 | Strong |
| `apps/inventory/repository.py` | 库存、台账、低库存和幂等读取 | Strong |
| `apps/inventory/router.py` | 路由与 RBAC | Strong |
| `apps/inventory/validator.py` | 非零调整校验 | Strong but narrow |
| `apps/procurement/services.py` | PO 收货与补货交界 | Strong |
| `apps/product/services.py` / `repository.py` | 产品库存旁路写风险 | Strong gap evidence |
| `templates/inventory.html` / `inventory_detail.html` | 库存展示与操作边界 | Medium |
| `templates/edit_inventory.html` / `adjust_inventory.html` | Edit 与 Adjust 分离 | Strong UX evidence |
| `templates/inventory_scan_action.html` | 扫码人工确认 | Strong UX evidence |
| `business_modules/inventory.md` | 库存权威边界与未落地目标 | Intent |
| `docs/reports/Business_Strong_A002_Inventory_Report.md` | 调整与台账闭环 | Strong |
| `docs/reports/Business_Strong_A003_Delivery_Report.md` | 创建不扣库存、Ship 扣库存 | Strong |
| `docs/reports/Business_Strong_A004_Purchase_Report.md` | 收货过账 | Strong |
| `docs/reports/Business_Strong_A018_Inventory_Ops_Report.md` | 操作诚实性 | Strong |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
