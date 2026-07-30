# 采购（Procurement）— Legacy Knowledge

**Evidence strength:** Strong（页面服务、持久化与业务门报告）/ Medium（跨 Finance 交界）  
**Domain identity:** Procurement owns `purchases` / `purchase_items`; Supplier 主数据由独立 Supplier 模块维护  
**Chain role:** 低库存 → 补货草稿 → 采购审批 → 收货入账 → 可选采购发票与应付  
**Verified:** 2026-07-23 against `H:\Workspace\EZAM_CRM - 9.0`（只读）

---

## 1. 范围与证据判断

可运行采购主链集中在 `apps/procurement`。旧模块规格仍把部分能力写在 `apps/purchase` 并保留早期表名风险描述，与当前实现不一致；本文件以运行路径为强证据，以旧规格为边界意图参考。

Supplier 只作为采购单的上游主数据被读取；收货通过 Inventory 写现存量与台账；采购发票和应付属于 Finance。横向 Approval 中心并未承接采购单审批，当前有效审批是采购详情下的 Type A 人工确认。

---

## 2. 业务规则

| ID | 规则描述 | 触发条件 | 例外/缺口 | EAOS 重写备注 |
|----|----------|----------|-----------|---------------|
| P-R1 | 新采购单使用 `PO` 加秒级时间戳编号，默认 Draft，头金额初始为零 | 手工建单或补货生成 | 同一秒并发的唯一性未见独立保证 | 使用受约束的编号服务 |
| P-R2 | 采购行金额由数量与成本单价相乘；头金额按行金额汇总 | 增加行；打开详情 | 头金额主要在查看详情时刷新 | 在写事务内维护汇总 |
| P-R3 | Draft、Open、Pending 被统一视为“开放阶段” | 增行、收货、删除及 KPI | Draft 因此可绕过审批直接收货 | 将可编辑、已审批、可收货拆成不同状态 |
| P-R4 | 低库存候选为现存量不高于安全库存的 SKU，按库存升序取有限条目 | 打开补货页 | 上限 20；没有 MOQ、交期或多供应商拆分 | 将补货策略显式化 |
| P-R5 | 有安全库存时，建议补到安全库存且至少 1；无安全库存时，以 10 为回补基线且至少 1 | 生成补货建议 | 是 Legacy 启发式，不是需求预测 | 不继承为默认企业策略 |
| P-R6 | 补货草稿必须选择供应商和至少一个正数量行；成本取产品当前成本价 | 生成 Draft PO | 不锁定报价或价格版本 | 记录价格来源与生效时点 |
| P-R7 | 补货仅生成 Draft 并转到审批页，不直接收货 | 补货提交成功 | 手工建单不强制立即进入审批 | 统一入口后的状态行为 |
| P-R8 | 本地审批只允许 Draft 且至少一行，并要求人工确认；成功后变为 Open | Type A Approve | 不创建 Approval 中心实例 | 选择唯一审批权威 |
| P-R9 | Approve 与 Receive 是两个动作；审批本身不改库存 | 审批成功 | Draft 仍可从另一路径直接 Receive | 服务端收货必须校验已释放状态 |
| P-R10 | 收货按每个有效正数量行增加 `inventory` 与产品镜像库存，并写 `PO Receipt` 台账，最后把 PO 标为 Received | Receive | 不写独立 `purchase_receipts` 单据 | 定义收货单或明确台账即凭证 |
| P-R11 | 相同 PO 的 `PO Receipt` 台账存在时拒绝再次收货 | Receive | 幂等键由交易类型和 `PO-{id}` 备注组成 | 使用唯一业务键/过账号 |
| P-R12 | 采购单仅在开放阶段且没有收货台账时可删除，并同时删除行 | Delete | Draft/Open/Pending 都满足“开放” | 优先取消与留痕 |
| P-R13 | 收货完成后 UI 才展示采购发票入口；Finance 创建采购发票并同步未付应付记录 | Create purchase invoice | 服务端未硬性要求 PO 已 Received | 跨域命令必须校验前置状态 |
| P-R14 | 同一 PO 已存在采购发票时拒绝重复创建 | Finance invoice create | 关联与权限仍在 Legacy Finance 路径 | 以唯一约束保护 |
| P-R15 | 列表开放 KPI 包含 Draft/Open/Pending；收货 KPI 包含 Received/已入库/Completed | 列表与仪表盘 | 中英文和历史值并存 | 使用规范枚举加显示翻译 |

---

## 3. 流程

### 3.1 低库存补货主链

1. Inventory 提供“现存量不高于安全库存”的候选。
2. 操作者选择供应商并确认正数量行。
3. 系统创建 Draft PO、复制建议行，并进入采购审批页。
4. 人工确认后 Draft → Open；此步不改库存。
5. Receive 校验采购单、阶段、行项及重复台账。
6. 对有效行增加库存、同步产品镜像值、写入库台账。
7. PO → Received；随后可进入 Finance 创建采购发票和应付。

### 3.2 手工采购

选择供应商 → 创建 Draft 头 → 在开放阶段增加产品行 → 可审批为 Open → 收货。

### 3.3 现存旁路

- Draft 被归入开放阶段，因此可不经 Approve 直接 Receive。
- Finance 发票入口虽在 UI 上以 Received 为条件显示，直接调用创建路径未见同等状态门。
- `/approvals` 只是导航目标，不会自动接收 PO 审批请求。

---

## 4. 校验

| ID | 校验 | 强度 | 说明 |
|----|------|------|------|
| P-V1 | 创建采购单必须有供应商 | Weak | 缺失时静默回列表 |
| P-V2 | 增行要求 PO 处于开放阶段 | Hard | 但开放阶段含 Draft |
| P-V3 | 行数量、成本价必须为正 | Absent/Weak | HTTP 要求字段；服务层未全面限制正值 |
| P-V4 | Receive 要求 PO 存在、处于开放阶段、有行且无重复收货台账 | Hard | 具有明确失败原因 |
| P-V5 | Receive 中产品和数量有效 | Weak | 非正数量或无产品的行被静默跳过 |
| P-V6 | Receive 必须能取得或建立库存记录 | Hard | 否则停止 |
| P-V7 | Delete 要求开放阶段且无收货台账 | Hard | 删除头与行 |
| P-V8 | 补货生成要求供应商和至少一个正数量行 | Hard | |
| P-V9 | Approve 仅限 Draft、有行且 `human_confirm=1` | Hard | |
| P-V10 | Receive 前必须已 Approve | Absent | Draft 可直接收货 |
| P-V11 | Finance 创建采购发票前必须 Received | Absent | UI 约束不是服务端约束 |
| P-V12 | Finance 创建采购发票必须具备相应权限 | Absent/Unclear | Legacy 创建路由未见等价硬门 |
| P-V13 | 同一 PO 不得重复采购发票 | Hard | 应用层查重 |
| P-V14 | 发票金额必须与当前行汇总一致 | Weak | 依赖头金额；未访问详情时可能未刷新 |
| P-V15 | Purchase360 访问权限 | Absent | 与普通详情页不一致 |
| P-V16 | `validate_purchase` 校验器 | Weak/Detached | 仅检查供应商，未接入页面主链 |

---

## 5. 数据含义

### 5.1 核心实体

| Entity | Meaning | Ownership |
|--------|---------|-----------|
| `purchases` | 采购单头、供应商、日期、汇总金额与状态 | Procurement |
| `purchase_items` | 产品、采购数量、成本单价与行金额 | Procurement |
| `suppliers` | 供方主数据 | Supplier；Procurement 只读引用 |
| `inventory` | 仓库现存量、安全库存与位置 | Inventory |
| `products.stock_qty` | 与库存并存的产品库存镜像 | Product/Legacy shared |
| `inventory_ledger` | 收货过账事实与过账后余额 | Inventory |
| `purchase_invoices` | 采购发票记录 | Finance |
| `ap_records` | 由采购发票形成的未付应付 | Finance |
| `purchase_receipts` | 规格/表结构中的收货实体 | 运行收货链未写入 |
| `purchase_requisitions` | 规格列出的请购实体 | 未观察到可运行读写链 |

### 5.2 关键字段语义

| Field | Meaning |
|-------|---------|
| `po_no` | Legacy 采购单号 |
| `supplier_id` | 供方引用 |
| `po_date` | 建单日期 |
| `total_amount` | 采购行金额汇总的头镜像 |
| `status` | Draft/Open/Pending/Received 等混合状态 |
| `qty` | 订购及收货使用的行数量；未观察到部分收货数量 |
| `cost_price` | 建行时的采购成本单价 |
| Ledger `trans_type` | 收货使用 `PO Receipt` |
| Ledger `remark` | 以 `PO-{purchase_id}` 关联采购单的字符串业务键 |
| Ledger `balance_qty` | 本行收货过账后的库存余额 |

### 5.3 状态含义

| Value / family | Legacy stage | Meaning |
|----------------|--------------|---------|
| Draft | open | 新建、可编辑；按设计待审批 |
| Open | open | 本地人工审批释放 |
| Pending | open | 历史兼容开放值，未见主要写入路径 |
| Received / 已入库 / Completed | received | 收货完成或历史等价值 |
| Other | other | 不参与标准收货链 |

---

## 6. 诚实缺口与风险

- **审批旁路：** 阶段归一化把 Draft 当作可收货状态，削弱了 Draft → Open 的人工门。
- **库存三写：** Receive 同时改 `inventory.stock_qty`、`products.stock_qty` 和 `inventory_ledger`；依赖单连接事务，但没有数据库级单一库存真相。
- **无部分收货模型：** 行数量被一次性全量入库，未见已收、待收或批次维度。
- **收货单缺席：** `purchase_receipts` 存在于结构/叙事，运行链只以台账证明收货。
- **发票前置门缺失：** Finance 创建路径可能在未收货或头金额陈旧时被直接调用。
- **双审批叙事：** 采购内置 Type A 会改状态，企业 Approval 中心没有运行连接。
- **文档漂移：** 早期模块规格中的包名、路由与表名描述不能代表当前运行事实。

---

## 7. 只读来源路径

| Path | Why cited | Strength |
|------|-----------|----------|
| `apps/procurement/services.py` | 建单、补货、审批、收货、删除规则 | Strong |
| `apps/procurement/repository.py` | 表、汇总、状态、收货幂等与低库存查询 | Strong |
| `apps/procurement/router.py` | 页面入口与 RBAC | Strong |
| `apps/procurement/validator.py` | 孤立的最小校验器 | Strong gap evidence |
| `apps/inventory/repository.py` | 收货使用的库存记录、镜像与台账接口 | Strong |
| `apps/finance/services.py` / `router.py` | 采购发票与 AP 交界 | Medium/Strong |
| `templates/purchases.html` / `purchase_detail.html` | 阶段操作与 UI 前置条件 | Medium |
| `templates/purchase_replenish.html` / `purchase_approve.html` | 补货与人工审批语义 | Strong UX evidence |
| `templates/purchase360.html` | 采购链展示及权限缺口 | Medium |
| `business_modules/procurement.md` | 边界意图；部分内容已过时 | Weak/Intent |
| `docs/reports/Business_Strong_A004_Purchase_Report.md` | 收货三写和删除保护 | Strong |
| `docs/reports/Business_Strong_A010_Purchase_Ops_Report.md` | 操作界面诚实性 | Strong |
| `docs/reports/V151E_Volume011_Supplier_Procurement_Business_Chain_Extraction_Report.md` | Supplier/Procurement 拆分历史 | Strong historical |

**Root:** `H:\Workspace\EZAM_CRM - 9.0\` + paths above.
